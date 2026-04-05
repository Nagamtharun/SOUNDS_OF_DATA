def value_to_rgb(value):
    """
    Maps an integer value (1-100) to a beautiful heatmap color gradient.
    Gradient transitions: Deep Blue -> Cyan -> Green -> Yellow -> Red
    """
    try:
        val = float(value)
    except:
        val = 1.0
        
    # Ensure value is clamped between 1 and 100
    val = max(1.0, min(100.0, val))
    
    # Normalize to 0.0 - 1.0
    t = (val - 1.0) / 99.0
    
    # Color stops for a nice heatmap
    stops = [
        (0.00, (0, 0, 139)),     # Dark Blue
        (0.20, (0, 100, 255)),   # Medium Blue
        (0.40, (0, 255, 255)),   # Cyan
        (0.60, (0, 255, 0)),     # Green
        (0.80, (255, 255, 0)),   # Yellow
        (1.00, (255, 0, 0))      # Red
    ]
    
    for i in range(len(stops) - 1):
        t1, c1 = stops[i]
        t2, c2 = stops[i+1]
        
        if t1 <= t <= t2:
            # Linear interpolation
            ratio = (t - t1) / (t2 - t1)
            r = int(c1[0] + (c2[0] - c1[0]) * ratio)
            g = int(c1[1] + (c2[1] - c1[1]) * ratio)
            b = int(c1[2] + (c2[2] - c1[2]) * ratio)
            return (r, g, b)
            
    return (255, 0, 0) # Fallback for exact 100
