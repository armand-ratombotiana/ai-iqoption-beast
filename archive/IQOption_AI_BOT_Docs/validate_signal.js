// Validate AI signal function
function validateSignal(signal) {
  if(signal !== 'CALL' && signal !== 'PUT') return false;
  return true;
}