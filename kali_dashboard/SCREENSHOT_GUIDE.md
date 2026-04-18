# KaliAgent Screenshot Guide

Complete guide for capturing and annotating documentation screenshots.

---

## Quick Start

### Automated Capture (Recommended)

```bash
# Install dependencies
pip install playwright
playwright install firefox

# Make script executable
chmod +x scripts/capture_screenshots.py

# Run capture script
python3 scripts/capture_screenshots.py
```

### Manual Capture

1. Open dashboard: `http://localhost:5173`
2. Navigate to each page
3. Press `PrintScreen` or use screenshot tool
4. Save with correct filename (see list below)

---

## Required Screenshots (15 Total)

### Dashboard Pages (6)

| # | Filename | Page URL | Description | Status |
|---|----------|----------|-------------|--------|
| 1 | `01-dashboard-overview.png` | `/` | Main dashboard with stats | ⚪ Pending |
| 2 | `02-engagements-page.png` | `/engagements` | Engagements list view | ⚪ Pending |
| 3 | `03-playbooks-page.png` | `/playbooks` | Available playbooks | ⚪ Pending |
| 4 | `04-tools-catalog.png` | `/tools` | 52 tools grid view | ⚪ Pending |
| 5 | `05-settings-safety.png` | `/settings` | Safety configuration | ⚪ Pending |
| 6 | `06-live-monitor.png` | `/live-monitor` | Real-time execution | ⚪ Pending |

### Workflow Screenshots (4)

| # | Filename | Page URL | Description | Status |
|---|----------|----------|-------------|--------|
| 7 | `07-create-engagement.png` | `/engagements/new` | Create new engagement form | ⚪ Pending |
| 8 | `08-execute-playbook.png` | `/playbooks/execute` | Playbook execution in progress | ⚪ Pending |
| 9 | `09-scan-results.png` | `/results` | Scan results with findings | ⚪ Pending |
| 10 | `10-pdf-report-preview.png` | `/reports/preview` | PDF report preview | ⚪ Pending |

### Detail Views (4)

| # | Filename | Page URL | Description | Status |
|---|----------|----------|-------------|--------|
| 11 | `11-tool-details.png` | `/tools/nmap` | Nmap tool detail page | ⚪ Pending |
| 12 | `12-authorization-settings.png` | `/settings/auth` | Authorization level config | ⚪ Pending |
| 13 | `13-audit-logs.png` | `/settings/audit` | Audit log viewer | ⚪ Pending |
| 14 | `14-test-coverage.png` | `/reports/tests` | Test coverage report | ⚪ Pending |

### Mobile View (1)

| # | Filename | Page URL | Description | Status |
|---|----------|----------|-------------|--------|
| 15 | `15-mobile-view.png` | `/` (mobile) | Responsive mobile layout | ⚪ Pending |

---

## Screenshot Specifications

### Resolution

| Device | Resolution | Use Case |
|--------|------------|----------|
| **Desktop** | 1920×1080 | Primary documentation |
| **Tablet** | 768×1024 | Optional (if showing responsive) |
| **Mobile** | 375×667 | Mobile view screenshot |

### Format

- **PNG** for UI screenshots (lossless, supports transparency)
- **JPG** for photos only (not applicable here)
- **WebP** for web optimization (optional)

### Quality Settings

```bash
# PNG compression (optipng)
optipng -o7 screenshot.png

# Or use pngquant for smaller size
pngquant --quality=65-80 screenshot.png
```

---

## Annotation Guidelines

### Tools

| Tool | Platform | Cost | Best For |
|------|----------|------|----------|
| **Flameshot** | Linux | Free | Quick annotations |
| **Snagit** | Windows/Mac | $50 | Professional edits |
| **GIMP** | All | Free | Advanced editing |
| **Canva** | Web | Free | Graphics & arrows |

### Annotation Standards

#### 1. Red Boxes for Focus Areas

```
┌─────────────────┐
│   Dashboard     │
│  ┌──────────┐   │  ← Red rectangle (2px stroke)
│  │  Stats   │   │
│  └──────────┘   │
└─────────────────┘
```

**Color:** `#FF0000` (pure red)  
**Stroke:** 2px solid  
**Corner Radius:** 0px (sharp corners)

---

#### 2. Numbered Callouts

```
   ① ② ③ ④ ⑤  ← Circled numbers (16px)
   ↓ ↓ ↓ ↓ ↓
  [Features]    ← Arrows pointing to elements
```

**Font:** Arial Bold  
**Size:** 16px for numbers, 12px for labels  
**Color:** White text on red circle  
**Circle:** 20px diameter, red fill

---

#### 3. Arrows for Workflows

```
Step 1 → Step 2 → Step 3
  ↓                  ↓
Action A          Action B
```

**Arrow Style:** Solid line, 2px  
**Arrow Head:** Filled triangle  
**Color:** `#FF0000` (red) or `#3b82f6` (blue)

---

#### 4. Blur Sensitive Data

```
Username: ████████     ← Blurred with Gaussian blur
Password: ████████     ← Radius: 5px
```

**Blur Type:** Gaussian  
**Radius:** 5-10px  
**Coverage:** Complete (no readable text)

---

## Step-by-Step Capture Process

### Step 1: Prepare Dashboard

```bash
# Start backend
cd kali_dashboard
python3 server.py &

# Start frontend
cd frontend
npm run dev

# Verify running
curl http://localhost:5173
```

---

### Step 2: Set Browser Resolution

**Firefox:**
1. Open `about:config`
2. Set `layout.css.devPixelsPerPx` to `1.0`
3. Press `F12` for DevTools
4. Click responsive design mode (`Ctrl+Shift+M`)
5. Set to `1920×1080`

**Chrome:**
1. Press `F12` for DevTools
2. Click device toolbar (`Ctrl+Shift+M`)
3. Select "Responsive"
4. Set to `1920×1080`

---

### Step 3: Capture Each Page

```bash
# Example for dashboard overview
firefox "http://localhost:5173/"

# Wait for load (3 seconds)
sleep 3

# Capture (Linux with scrot)
scrot -d 1 screenshots/01-dashboard-overview.png

# Or use Flameshot for annotations
flameshot gui -p screenshots/01-dashboard-overview.png
```

---

### Step 4: Add Annotations

**Using Flameshot:**

```bash
# Launch Flameshot
flameshot gui

# Keyboard shortcuts:
# R - Rectangle
# C - Circle
# T - Text
# A - Arrow
# B - Blur
# S - Save
```

**Using GIMP:**

1. Open screenshot in GIMP
2. Add new layer for annotations
3. Use Rectangle Select Tool
4. Stroke Selection (2px, red)
5. Add Text Tool for labels
6. Export as PNG

---

### Step 5: Optimize File Size

```bash
# Install optipng
sudo apt install optipng

# Optimize all screenshots
cd screenshots
for file in *.png; do
    optipng -o7 "$file"
done

# Check file sizes
ls -lh *.png
```

**Target Sizes:**
- Desktop screenshots: 200-500 KB
- Mobile screenshots: 100-300 KB
- Thumbnails: 50-100 KB

---

## Screenshot Checklist

### Before Capture

- [ ] Dashboard is running (`http://localhost:5173`)
- [ ] Backend is running (`http://localhost:8001`)
- [ ] Browser resolution set to 1920×1080
- [ ] Notifications disabled
- [ ] Bookmarks bar hidden
- [ ] Clean browser profile (no personal data)

### During Capture

- [ ] Each page fully loaded before capture
- [ ] No loading spinners visible
- [ ] All data populated (no "Loading..." text)
- [ ] Consistent lighting/theme across shots
- [ ] No mouse cursor in screenshot (unless demonstrating)

### After Capture

- [ ] All 15 screenshots captured
- [ ] Filenames match specification
- [ ] Annotations added where needed
- [ ] File sizes optimized (<500KB each)
- [ ] Screenshots reviewed for quality
- [ ] Sensitive data blurred (if any)

---

## Troubleshooting

### Issue: Dashboard Not Loading

**Solution:**
```bash
# Check backend
curl http://localhost:8001/api/health

# Check frontend
curl http://localhost:5173

# Restart if needed
pkill -f "python3 server.py"
pkill -f "npm run dev"

# Start fresh
cd kali_dashboard
python3 server.py &
cd frontend
npm run dev
```

---

### Issue: Screenshot Too Dark

**Cause:** Browser dark theme + OS dark theme

**Solution:**
```css
/* Add to browser userContent.css */
@media (prefers-color-scheme: dark) {
  :root {
    color-scheme: light dark;
  }
}
```

Or temporarily switch OS to light theme for capture.

---

### Issue: File Size Too Large

**Solution:**
```bash
# Compress with pngquant
pngquant --quality=65-80 --output=output.png input.png

# Or resize if too large
convert input.png -resize 1920x1080 output.png
```

---

## Example Annotated Screenshot

```
╔═══════════════════════════════════════════════════════════╗
║  KALIAGENT DASHBOARD                          🔔 👤 ⚙️    ║
╠═══════════════════════════════════════════════════════════╣
║                                                           ║
║  📊 Quick Actions         ┌─────────────────────────┐    ║
║     ┌──────────┐          │   📈 Engagement Stats   │    ║
║     │ + New    │  ← ①     │                         │    ║
║     │ Engage.  │          │   Total: 42             │    ║
║     └──────────┘          │   Active: 3             │    ║
║                           │   Completed: 39         │    ║
║     ┌──────────┐          └─────────────────────────┘    ║
║     │ Execute  │  ← ②                                    ║
║     │ Playbook │                                         ║
║     └──────────┘          ┌─────────────────────────┐    ║
║                           │   🛡️  Safety Status     │    ║
║     ┌──────────┐          │                         │    ║
║     │ View     │  ← ③     │   Whitelist: ✅ Active  │    ║
║     │ Reports  │          │   Blacklist: ✅ Active  │    ║
║     └──────────┘          │   Audit Log: ✅ Active  │    ║
║                           └─────────────────────────┘    ║
║                                                           ║
║  ┌─────────────────────────────────────────────────────┐ ║
║  │  📋 Recent Engagements                              │ ║
║  │                                                     │ ║
║  │  1. Q2 External Pentest    ✅ Completed   Today    │ ║
║  │  2. Web App Audit          🟡 In Progress Today    │ ║
║  │  3. Internal Network Scan  ⏳ Pending     Yesterday│ ║
║  └─────────────────────────────────────────────────────┘ ║
╚═══════════════════════════════════════════════════════════╝

Callouts:
① Create new engagement button
② Execute playbook quick action
③ View reports shortcut
```

---

## Storage & Organization

### Directory Structure

```
kali_dashboard/
├── screenshots/
│   ├── raw/              # Original unedited captures
│   │   ├── 01-dashboard-overview.png
│   │   └── ...
│   ├── annotated/        # With red boxes, arrows, numbers
│   │   ├── 01-dashboard-overview.png
│   │   └── ...
│   └── thumbnails/       # 640×360 for quick previews
│       ├── 01-dashboard-overview.png
│       └── ...
└── SCREENSHOT_GUIDE.md
```

### Naming Convention

```
{number}-{page}-{description}.png

Examples:
01-dashboard-overview.png
07-create-engagement.png
15-mobile-view.png
```

---

## Usage in Documentation

### Markdown Syntax

```markdown
![Dashboard Overview](screenshots/01-dashboard-overview.png)
*Figure 1: Main dashboard showing engagement statistics and quick actions*
```

### With Caption

```markdown
<figure>
  <img src="screenshots/01-dashboard-overview.png" 
       alt="KaliAgent Dashboard Overview" 
       width="1920">
  <figcaption>
    Figure 1: Main dashboard showing engagement statistics, 
    quick actions, and recent engagements.
  </figcaption>
</figure>
```

### Responsive Image

```markdown
<picture>
  <source media="(max-width: 768px)" 
          srcset="screenshots/thumbnails/01-dashboard-overview.png">
  <img src="screenshots/01-dashboard-overview.png" 
       alt="Dashboard Overview" 
       loading="lazy">
</picture>
```

---

## Quality Control

### Review Checklist

For each screenshot:

- [ ] Resolution is 1920×1080 (or 375×667 for mobile)
- [ ] All UI elements are sharp and clear
- [ ] No loading spinners or "Loading..." text
- [ ] Annotations are clear (2px red lines)
- [ ] Numbers are readable (16px minimum)
- [ ] Arrows point to correct elements
- [ ] Sensitive data is blurred
- [ ] File size is under 500 KB
- [ ] Filename matches specification
- [ ] Alt text is descriptive

### Approval Process

1. Capture all 15 screenshots
2. Add annotations
3. Optimize file sizes
4. Review against checklist
5. Commit to Git
6. Update documentation references

---

## Tools & Resources

### Recommended Software

| Purpose | Tool | Platform | Cost |
|---------|------|----------|------|
| **Capture** | Flameshot | Linux | Free |
| **Capture** | Snipping Tool | Windows | Free |
| **Capture** | Cmd+Shift+4 | macOS | Free |
| **Edit** | GIMP | All | Free |
| **Edit** | Photoshop | All | $20/mo |
| **Annotate** | Canva | Web | Free |
| **Compress** | TinyPNG | Web | Free tier |
| **Compress** | optipng | CLI | Free |

### Browser Extensions

- **Full Page Screen Capture** (Chrome/Firefox)
- **Fireshot** (Chrome/Firefox)
- **Nimbus Screenshot** (Chrome/Firefox)

---

## Contact & Support

Need help with screenshots?

- **Documentation:** `/kali_dashboard/SCREENSHOT_GUIDE.md`
- **Script:** `python3 scripts/capture_screenshots.py`
- **Examples:** See `screenshots/annotated/` directory

---

*Last Updated: April 18, 2026*  
*Version: 1.0.0*
