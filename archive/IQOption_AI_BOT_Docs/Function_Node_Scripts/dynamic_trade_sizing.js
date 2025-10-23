// Dynamic trade sizing + martingale logic
function calculateTradeAmount(base, confidence, level) {
  return Math.min(base * Math.pow(1.5, level) * (confidence/100), base*5);
}