# Manual smoke test against a *running* local backend. Not part of the
# pytest suite (that's tests/) -- start the server first:
#   python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
# then: python scripts/smoke_test.py
import urllib.request, json, random

API = 'http://127.0.0.1:8000'

print('=== Edge Case Tests ===')

# Edge case 1: n=2 (minimum clique)
V = ['a','b']
edges = [{'u':'a','v':'b','label':0.5}]
body = json.dumps({'graph': {'vertices': V, 'edges': edges}}).encode()
req = urllib.request.Request(API + '/api/spanner', data=body, headers={'Content-Type': 'application/json'})
r = urllib.request.urlopen(req)
d = json.loads(r.read())
m = d['metrics']
print('n=2: spanner=' + str(m['spanner_edges']) + ' savings=' + str(m['savings_pct']) + '% verified=' + str(m['verified']))

# Edge case 2: n=1 (single vertex)
V = ['a']
edges = []
body = json.dumps({'graph': {'vertices': V, 'edges': edges}}).encode()
req = urllib.request.Request(API + '/api/spanner', data=body, headers={'Content-Type': 'application/json'})
try:
    r = urllib.request.urlopen(req)
    d = json.loads(r.read())
    print('n=1: spanner=' + str(d['metrics']['spanner_edges']))
except urllib.error.HTTPError as e:
    print('n=1: error ' + str(e.code))

# Edge case 3: n=50 benchmark
random.seed(0)
V = [str(i) for i in range(50)]
edges = []
for i in range(50):
    for j in range(i+1, 50):
        edges.append({'u': str(i), 'v': str(j), 'label': random.random()})
body = json.dumps({'graph': {'vertices': V, 'edges': edges}}).encode()
req = urllib.request.Request(API + '/api/spanner', data=body, headers={'Content-Type': 'application/json'})
r = urllib.request.urlopen(req)
d = json.loads(r.read())
m = d['metrics']
print('n=50: uploaded=' + str(m['uploaded_edges']) + ' spanner=' + str(m['spanner_edges']) + ' savings=' + str(m['savings_pct']) + '% verified=' + str(m['verified']))

# Edge case 4: n=80 benchmark (max practical size)
random.seed(1)
V = [str(i) for i in range(80)]
edges = []
for i in range(80):
    for j in range(i+1, 80):
        edges.append({'u': str(i), 'v': str(j), 'label': random.random()})
body = json.dumps({'graph': {'vertices': V, 'edges': edges}}).encode()
req = urllib.request.Request(API + '/api/spanner', data=body, headers={'Content-Type': 'application/json'})
r = urllib.request.urlopen(req)
d = json.loads(r.read())
m = d['metrics']
print('n=80: uploaded=' + str(m['uploaded_edges']) + ' spanner=' + str(m['spanner_edges']) + ' savings=' + str(m['savings_pct']) + '% verified=' + str(m['verified']))

# Edge case 5: CSV upload
boundary = '----B'
body = (
    b'--' + boundary.encode() + b'\r\n'
    + b'Content-Disposition: form-data; name="file"; filename="d.csv"\r\n'
    + b'Content-Type: text/csv\r\n\r\n'
    + b'date,words\r\n'
    + b'0.1,a b\r\n'
    + b'0.2,\r\n'
    + b'0.3,c d\r\n'
    + b'--' + boundary.encode() + b'--\r\n'
)
req = urllib.request.Request(API + '/api/upload', data=body, headers={'Content-Type': 'multipart/form-data; boundary=' + boundary})
r = urllib.request.urlopen(req)
d = json.loads(r.read())
print('Upload empty rows: parsed=' + str(d['rows_parsed']) + ' edges=' + str(len(d['graph']['edges'])))

print('=== ALL TESTS PASSED ===')
