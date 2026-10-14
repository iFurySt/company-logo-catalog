#!/usr/bin/env node
/** Audits availability only. Successful image bytes never verify issuer identity. */
import { Agent, get } from 'node:https';
import { readFileSync, writeFileSync, mkdirSync, existsSync, appendFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { dirname, resolve as resolvePath } from 'node:path';
import { pathToFileURL } from 'node:url';

export function sourceURL(symbol) {
  if (typeof symbol !== 'string' || !/^[A-Z0-9][A-Z0-9.$/ -]{0,39}$/.test(symbol) || symbol.trim() !== symbol || symbol.split('/').includes('..'))
    throw Error('Invalid public stock symbol.');
  return 'https://financialmodelingprep.com/image-stock/' + encodeURIComponent(symbol) + '.png';
}
export function imageMetadata(bytes, mime) {
  if (mime?.split(';')[0] !== 'image/png') throw Error('unsupported-mime');
  if (bytes.length > 262144) throw Error('size-limit');
  if (bytes.length < 33 || !bytes.subarray(0, 8).equals(Buffer.from([137, 80, 78, 71, 13, 10, 26, 10])) || bytes.toString('ascii', 12, 16) !== 'IHDR')
    throw Error('invalid-png-header');
  const width = bytes.readUInt32BE(16), height = bytes.readUInt32BE(20);
  if (width < 4 || height < 4 || width > 2048 || height > 2048) throw Error('invalid-dimensions');
  return { sha256: createHash('sha256').update(bytes).digest('hex'), width, height, format: 'png', bytes: bytes.length };
}
export function parseOptions(args) {
  const allowed = new Set(['input', 'output', 'images', 'workers', 'rate', 'timeout', 'retry-errors']);
  const options = {};
  for (let i = 0; i < args.length; i++) {
    const name = args[i].replace(/^--/, '');
    if (!args[i].startsWith('--') || !allowed.has(name) || name in options) throw Error('Unknown/duplicate option.');
    if (name === 'retry-errors') options[name] = true;
    else { if (!args[i + 1] || args[i + 1].startsWith('--')) throw Error('Missing option value.'); options[name] = args[++i]; }
  }
  if (!options.input || !options.output) throw Error('Use --input directory.json --output private-results.jsonl [--images private-folder].');
  options.workers = Number(options.workers ?? 4); options.rate = Number(options.rate ?? 2); options.timeout = Number(options.timeout ?? 20000);
  if (!Number.isInteger(options.workers) || options.workers < 1 || options.workers > 8 || !Number.isFinite(options.rate) || options.rate < .5 || options.rate > 4 || !Number.isInteger(options.timeout) || options.timeout < 2000 || options.timeout > 30000)
    throw Error('Bounded workers 1..8, rate 0.5..4/s, timeout 2000..30000ms required.');
  return options;
}
export function readCheckpoint(path) {
  const rows = new Map();
  if (!existsSync(path)) return rows;
  for (const line of readFileSync(path, 'utf8').split('\n').filter(Boolean)) {
    const row = JSON.parse(line);
    if (row.url !== sourceURL(row.symbol) || typeof row.result !== 'string') throw Error('Invalid checkpoint.');
    rows.set(row.symbol, row);
  }
  return rows;
}
export async function scan(options, requestAsset = get) {
  const input = JSON.parse(readFileSync(options.input, 'utf8'));
  const rows = Array.isArray(input) ? input : input.securities;
  if (!Array.isArray(rows) || rows.length > 30000) throw Error('Invalid directory input.');
  const symbols = rows.map(row => { sourceURL(row.symbol); return row.symbol; });
  if (new Set(symbols).size !== symbols.length) throw Error('Duplicate directory symbols.');
  const last = readCheckpoint(options.output);
  const retryable = new Set(['timeout', 'network-error', 'http-error', 'rate-limited']);
  const todo = symbols.filter(symbol => !last.has(symbol) || options['retry-errors'] && retryable.has(last.get(symbol).result));
  mkdirSync(dirname(resolvePath(options.output)), { recursive: true, mode: 0o700 });
  if (options.images) mkdirSync(options.images, { recursive: true, mode: 0o700 });
  const agent = new Agent({ keepAlive: true, maxSockets: options.workers, proxyEnv: process.env });
  const shutdown = new AbortController();
  let cursor = 0, nextAt = 0, stopped = false;
  const stop = () => { stopped = true; shutdown.abort(); };
  process.once('SIGINT', stop); process.once('SIGTERM', stop);
  const tick = () => new Promise(resolve => { const when = Math.max(Date.now(), nextAt); nextAt = when + 1000 / options.rate; setTimeout(resolve, when - Date.now()); });
  async function probe(symbol) {
    await tick();
    if (shutdown.signal.aborted) return null;
    const url = sourceURL(symbol), checkedAt = new Date().toISOString(), start = Date.now();
    return new Promise(resolve => {
      let settled = false;
      const finish = value => { if (!settled) { settled = true; resolve(shutdown.signal.aborted ? null : { symbol, url, checkedAt, elapsedMs: Date.now() - start, ...value }); } };
      const request = requestAsset(url, { agent, signal: AbortSignal.any([AbortSignal.timeout(options.timeout), shutdown.signal]), headers: { 'User-Agent': 'CompanyLogoCatalog (+https://github.com/ifuryst/company-logo-catalog)', Accept: 'image/png' } }, response => {
        const httpStatus = response.statusCode;
        if ([403, 429].includes(httpStatus)) { stopped = true; response.resume(); finish({ result: 'rate-limited', httpStatus }); return; }
        if (httpStatus !== 200) { response.resume(); finish({ result: httpStatus === 404 ? 'not-found' : 'http-error', httpStatus }); return; }
        const mime = response.headers['content-type'];
        if (mime?.split(';')[0] !== 'image/png' || Number(response.headers['content-length'] || 0) > 262144) {
          response.resume(); finish({ result: 'rejected-image', httpStatus, mime, rejectReason: mime?.split(';')[0] !== 'image/png' ? 'unsupported-mime' : 'size-limit' }); return;
        }
        const chunks = []; let size = 0;
        response.on('data', chunk => { size += chunk.length; if (size > 262144) { response.destroy(); finish({ result: 'rejected-image', httpStatus, mime, rejectReason: 'size-limit' }); } else chunks.push(chunk); });
        response.on('end', () => {
          const bytes = Buffer.concat(chunks);
          try {
            const metadata = imageMetadata(bytes, mime);
            if (options.images) writeFileSync(resolvePath(options.images, metadata.sha256 + '.png'), bytes, { mode: 0o600 });
            finish({ result: 'png-unverified', httpStatus, mime, ...metadata });
          } catch (error) { finish({ result: 'rejected-image', httpStatus, mime, rejectReason: error.message }); }
        });
        response.on('error', error => finish({ result: 'network-error', error: error.name }));
      });
      request.on('error', error => finish({ result: error.name === 'AbortError' ? 'timeout' : 'network-error', error: error.name }));
    });
  }
  console.log(JSON.stringify({ total: symbols.length, pending: todo.length, status: 'availability-only' }));
  try {
    await Promise.all(Array.from({ length: options.workers }, async () => {
      while (cursor < todo.length && !stopped) {
        const symbol = todo[cursor++]; let result = await probe(symbol);
        if (result && retryable.has(result.result) && !stopped) { result = await probe(symbol); if (result) result.attempts = 2; }
        else if (result) result.attempts = 1;
        if (!result) continue;
        appendFileSync(options.output, JSON.stringify(result) + '\n', { mode: 0o600 }); last.set(symbol, result);
        if (cursor % 50 === 0) console.log(JSON.stringify({ completed: symbols.filter(s => last.has(s)).length, total: symbols.length }));
      }
    }));
  } finally { agent.destroy(); process.removeListener('SIGINT', stop); process.removeListener('SIGTERM', stop); }
  const summary = { completed: symbols.filter(s => last.has(s)).length, total: symbols.length, stopped };
  console.log(JSON.stringify(summary)); return summary;
}
if (process.argv[1] && import.meta.url === pathToFileURL(resolvePath(process.argv[1])).href) {
  try { const result = await scan(parseOptions(process.argv.slice(2))); if (result.stopped || result.completed < result.total) process.exitCode = 2; }
  catch (error) { console.error(error.message); process.exitCode = 1; }
}
