// Execute trade only if confidence > threshold
function shouldExecute(confidence, threshold=70){ return confidence >= threshold; }