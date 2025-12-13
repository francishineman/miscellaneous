import json
from flask import Flask, jsonify, request

app = Flask(__name__)

tests = [
  { 'id': 1, 'name': 'Feature' },
  { 'id': 2, 'name': 'Performance' },
  { 'id': 3, 'name': 'End2End' }
]

nextTestCaseId = 4

@app.route('/tests', methods=['GET'])
def get_tests():
  return jsonify(tests)

@app.route('/tests/<int:id>', methods=['GET'])
def get_test_by_id(id: int):
  test = get_test(id)
  if test is None:
    return jsonify({ 'error': 'test does not exist'}), 404
  return jsonify(test)

def get_test(id):
  return next((e for e in tests if e['id'] == id), None)

def test_is_valid(test):
  for key in test.keys():
    if key != 'name':
      return False
  return True

@app.route('/tests', methods=['POST'])
def create_test():
  global nexttestId
  test = json.loads(request.data)
  if not test_is_valid(test):
    return jsonify({ 'error': 'Invalid test properties.' }), 400

  test['id'] = nexttestId
  nexttestId += 1
  tests.append(test)

  return '', 201, { 'location': f'/tests/{test["id"]}' }

@app.route('/tests/<int:id>', methods=['PUT'])
def update_test(id: int):
  test = get_test(id)
  if test is None:
    return jsonify({ 'error': 'test does not exist.' }), 404

  updated_test = json.loads(request.data)
  if not test_is_valid(updated_test):
    return jsonify({ 'error': 'Invalid test properties.' }), 400

  test.update(updated_test)

  return jsonify(test)

@app.route('/tests/<int:id>', methods=['DELETE'])
def delete_test(id: int):
  global tests
  test = get_test(id)
  if test is None:
    return jsonify({ 'error': 'test does not exist.' }), 404

  tests = [e for e in tests if e['id'] != id]
  return jsonify(test), 200

app.run()
