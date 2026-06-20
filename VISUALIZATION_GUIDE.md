# 🚁 Fly-In Visualization Guide

This project now has **TWO visualization modes**:

## 1. **Terminal ASCII Visualization** (Minimal Dependencies)

### Run:
```bash
python3 run_with_visualization.py map.txt
```

### Features:
- ✅ Text-based output in terminal
- ✅ Real-time zone and drone status updates
- ✅ Color-coded zones (ANSI colors)
- ✅ Capacity tracking
- ✅ Turn-by-turn logs
- ✅ No external GUI libraries needed (besides Pydantic)

### What You See:
```
╔════════════════════════════════════════════════════════════════╗
║         🚁 FLY-IN DRONE SIMULATION - TURN 1                   ║
╚════════════════════════════════════════════════════════════════╝

📍 ZONES AND DRONES:
┌──────────┐
│ 🟢 start │
│ Cap: 0/1 │
│ D0,D1    │
└──────────┘

📡 CONNECTIONS:
  start ━━━━ junction (capacity: 1)

🚁 DRONE STATUS:
  D0: Zone=start Status=→ MOVING Path_remaining=3

📊 STATISTICS:
  ✓ Delivered: 0/3 | ⏳ In Transit: 0 | → Moving: 3
```

---

## 2. **Graphical GUI Visualization** (Pygame)

### Run:
```bash
python3 run_graphical.py map.txt
```

### Requirements:
```bash
pip install pygame
```

### Features:
- ✅ Interactive graphical window
- ✅ Zones displayed as colored circles (nodes)
- ✅ Connections shown as lines between zones
- ✅ **Drones animated** moving smoothly between zones
- ✅ Real-time statistics display
- ✅ Pausable simulation (SPACE key)
- ✅ Smooth 60 FPS animation
- ✅ Color-coded drone status (→ Moving, ⏳ In Transit, ✓ Delivered)

### Controls:
- **SPACE** - Pause/Resume animation
- **Q** - Quit simulation
- **Close Window** - Exit

### What You See:
A window displaying:
- Network nodes (zones) as colored circles
- Drones as smaller colored circles with ID
- Connections as gray lines
- Real-time turn counter and delivery stats
- Animated drone movement between zones

---

## Comparison

| Feature | Terminal | Graphical |
|---------|----------|-----------|
| Installation | None (uses Pydantic) | `pip install pygame` |
| Visual Appeal | Text-based | Full GUI with animations |
| Interaction | None | Pausable, keyboard controls |
| Performance | Fast | 60 FPS smooth |
| Suitable for | Servers, CI/CD | Desktop testing, demos |
| Setup Complexity | Simple | Easy |

---

## Troubleshooting

### Terminal Version Issues:
- **Colors not showing?** - Your terminal may not support ANSI colors. Try a modern terminal (iTerm2, GNOME Terminal, Windows Terminal).

### Graphical Version Issues:
- **Pygame not found?** - Run `pip install pygame`
- **Window won't open?** - Check your display. Graphical mode requires a display server.
- **Slow animation?** - Reduce monitor Hz or check CPU usage

---

## File Structure

```
Fly-in/
├── fly-in.py                      # Original entry point
├── run_with_visualization.py      # Terminal ASCII runner
├── run_graphical.py               # Graphical GUI runner
├── visualizer.py                  # Terminal ASCII visualizer
├── graphical_visualizer.py        # Pygame visualizer (NEW!)
├── simulation.py                  # Original simulation
├── objects.py                     # Original domain objects
└── ... (other original files)
```

---

## Next Steps

Choose your visualization:

### For Terminal-based output:
```bash
python3 run_with_visualization.py map.txt
```

### For Interactive GUI:
```bash
python3 run_graphical.py map.txt
```

### For original (no visualization):
```bash
python3 fly-in.py map.txt
```

All three work independently - **no original files were modified**.

