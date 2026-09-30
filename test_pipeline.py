import subprocess, sys, time, http.client, json

proc = subprocess.Popen([sys.executable, 'backend/main.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
time.sleep(3)

def call(method, path, body=None):
    conn = http.client.HTTPConnection('127.0.0.1', 8000, timeout=10)
    headers = {}
    b = None
    if body:
        b = json.dumps(body).encode()
        headers['Content-Type'] = 'application/json'
    conn.request(method, path, b, headers)
    resp = conn.getresponse()
    data = resp.read().decode()
    conn.close()
    return resp.status, data

try:
    print('1. Health...')
    s, d = call('GET', '/health')
    assert s == 200, 'Health failed'
    print('   OK')

    print('2. Create project...')
    s, d = call('POST', '/projects', {'name': 'Test Project', 'topic': 'Blue whales', 'language': 'en', 'platform': 'tiktok'})
    assert s == 200, f'Create failed: {d}'
    pid = json.loads(d)['id']
    print(f'   OK: {pid[:8]}')

    print('3. Generate hooks...')
    s, d = call('POST', f'/projects/{pid}/generate-hooks')
    assert s == 200, f'Hooks failed: {d}'
    hooks = json.loads(d)['options']
    print(f'   OK: {len(hooks)} hooks')

    print('4. Select hook...')
    s, d = call('POST', f'/projects/{pid}/select-hook', {'hook': hooks[0]})
    assert s == 200, f'Select failed: {d}'
    print('   OK')

    print('5. Generate content...')
    s, d = call('POST', f'/projects/{pid}/generate-content')
    assert s == 200, f'Content failed: {d}'
    scenes = json.loads(d)['scenes']
    print(f'   OK: {len(scenes)} scenes')

    print('6. Generate images...')
    s, d = call('POST', f'/projects/{pid}/images/generate')
    assert s == 200, f'Images failed: {d}'
    print('   OK')

    print('7. Generate TTS...')
    s, d = call('POST', f'/projects/{pid}/tts')
    assert s == 200, f'TTS failed: {d}'
    dur = json.loads(d)['duration']
    print(f'   OK: {dur:.2f}s')

    print('8. Build timeline...')
    s, d = call('POST', f'/projects/{pid}/timeline')
    assert s == 200, f'Timeline failed: {d}'
    print('   OK')

    print('9. Final package...')
    s, d = call('GET', f'/projects/{pid}/package')
    assert s == 200, f'Package failed: {d}'
    print('   OK')

    print('')
    print('ALL BACKEND PIPELINE TESTS PASSED!')

except Exception as e:
    print(f'TEST FAILED: {e}')
    import traceback
    traceback.print_exc()

finally:
    proc.terminate()
    proc.wait()
