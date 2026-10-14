import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, writeFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { sourceURL, imageMetadata, parseOptions, readCheckpoint } from '../scripts/probe-logos.mjs';
const png = Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAgAAAAICAYAAADED76LAAAAFklEQVR4nGNgYGD4z0AHYBxVSF+FAABtDwH/G+n3EgAAAABJRU5ErkJggg==', 'base64');
test('requests only an encoded symbol on the fixed source', () => {
  assert.equal(sourceURL('PCG$X'), 'https://financialmodelingprep.com/image-stock/PCG%24X.png');
  assert.equal(sourceURL('BRK/B'), 'https://financialmodelingprep.com/image-stock/BRK%2FB.png');
  for (const symbol of ['https://evil.example', 'A/../B', 'KEY?token=secret', ' A', 'A\n']) assert.throws(() => sourceURL(symbol));
});
test('image bounds reject HTML, wrong MIME, tiny/huge dimensions and overflow', () => {
  assert.equal(imageMetadata(png, 'image/png').width, 8);
  assert.equal(imageMetadata(png, 'image/png; charset=binary').format, 'png');
  assert.throws(() => imageMetadata(Buffer.from('<svg/>'), 'image/svg+xml'));
  const tiny=Buffer.from(png);tiny.writeUInt32BE(1,16);assert.throws(()=>imageMetadata(tiny,'image/png'));
  const huge=Buffer.from(png);huge.writeUInt32BE(4096,20);assert.throws(()=>imageMetadata(huge,'image/png'));
  assert.throws(()=>imageMetadata(Buffer.alloc(262145),'image/png'));
});
test('workload limits and missing/unknown/duplicate arguments are rejected', () => {
  assert.equal(parseOptions(['--input','in','--output','out']).workers,4);
  for(const suffix of [['--workers','9'],['--rate','10'],['--timeout','99999'],['--endpoint','https://evil.example'],['--workers'],['--input','again']])
    assert.throws(()=>parseOptions(['--input','in','--output','out',...suffix]));
});
test('checkpoint resumes exact symbols and the last retry, refusing wrong provider URLs', () => {
  const dir=mkdtempSync(join(tmpdir(),'logo-probe-'));
  try {const path=join(dir,'results.jsonl');assert.equal(readCheckpoint(path).size,0);
    writeFileSync(path, [{symbol:'A',url:sourceURL('A'),result:'timeout'},{symbol:'A',url:sourceURL('A'),result:'png-unverified'}].map(r=>JSON.stringify(r)).join('\n'));
    assert.equal(readCheckpoint(path).get('A').result,'png-unverified');
    writeFileSync(path,JSON.stringify({symbol:'A',url:'https://evil.example',result:'png-unverified'}));assert.throws(()=>readCheckpoint(path));
  } finally{rmSync(dir,{recursive:true,force:true});}
});

test('actual scan writes cache/checkpoint and resumes without a second HTTP request', async () => {
  const { scan } = await import('../scripts/probe-logos.mjs');
  const { PassThrough } = await import('node:stream');
  const { EventEmitter } = await import('node:events');
  const { readFileSync, readdirSync } = await import('node:fs');
  const dir=mkdtempSync(join(tmpdir(),'logo-scan-'));
  try {
    const input=join(dir,'input.json'),output=join(dir,'results.jsonl'),images=join(dir,'images');
    writeFileSync(input,JSON.stringify([{symbol:'EX'}]));let calls=0;
    const request=(_url,_options,receive)=>{
      calls++;const emitter=new EventEmitter();queueMicrotask(()=>{
        const response=new PassThrough();response.statusCode=200;response.headers={'content-type':'image/png'};
        receive(response);response.end(png);
      });return emitter;
    };
    const options=parseOptions(['--input',input,'--output',output,'--images',images,'--workers','1','--rate','4']);
    assert.equal((await scan(options,request)).completed,1);
    assert.equal(readCheckpoint(output).get('EX').result,'png-unverified');
    const [file]=readdirSync(images);assert.ok(file.endsWith('.png'));assert.deepEqual(readFileSync(join(images,file)),png);
    assert.equal((await scan(options,request)).completed,1);assert.equal(calls,1);
  }finally{rmSync(dir,{recursive:true,force:true});}
});

test('provider rejection stops a batch instead of bypassing its access limit', async()=>{
  const {scan}=await import('../scripts/probe-logos.mjs');const {PassThrough}=await import('node:stream');const{EventEmitter}=await import('node:events');
  const dir=mkdtempSync(join(tmpdir(),'logo-stop-'));
  try{
    const input=join(dir,'input.json'),output=join(dir,'results.jsonl');writeFileSync(input,JSON.stringify([{symbol:'EX'},{symbol:'NEXT'}]));let calls=0;
    const request=(_url,_options,receive)=>{calls++;const emitter=new EventEmitter();queueMicrotask(()=>{const response=new PassThrough();response.statusCode=429;response.headers={};receive(response);response.end();});return emitter;};
    const result=await scan(parseOptions(['--input',input,'--output',output,'--workers','1','--rate','4']),request);
    assert.equal(result.stopped,true);assert.equal(result.completed,1);assert.equal(calls,1);assert.equal(readCheckpoint(output).get('EX').result,'rate-limited');
  }finally{rmSync(dir,{recursive:true,force:true});}
});
