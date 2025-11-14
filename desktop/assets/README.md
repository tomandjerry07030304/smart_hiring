# Icon Placeholder Files

The desktop application requires the following icon files in this directory:

## Required Icons

### 1. icon.ico (Windows Icon)
- **Format**: ICO (Windows Icon)
- **Sizes**: 16x16, 32x32, 48x48, 256x256 (multi-resolution)
- **Usage**: Application icon, taskbar, window title bar
- **Tool**: Use online converter or tools like:
  - [ICO Convert](https://icoconvert.com/)
  - [RealFaviconGenerator](https://realfavicongenerator.net/)
  - Adobe Photoshop/GIMP with ICO plugin

### 2. icon.png (High-Res PNG)
- **Format**: PNG
- **Size**: 512x512 or 1024x1024
- **Usage**: Source for all other icons, macOS icon generation
- **Requirements**: Transparent background preferred

### 3. logo.png (Installer Banner)
- **Format**: PNG
- **Size**: 164x314 (NSIS standard) or 600x400
- **Usage**: NSIS installer sidebar image
- **Requirements**: Professional looking, brand colors

## Temporary Workaround

Until you create custom icons, the build will use electron-builder's default icon. To add your icons:

1. **Create or source your icon** (logo, brand mark)
2. **Convert to required formats** using online tools
3. **Place in this directory**: `desktop/assets/`
4. **Rebuild the application**

## Design Guidelines

### Logo/Icon Design Tips
- **Simple & Recognizable**: Works at small sizes (16x16)
- **Professional**: Represents your brand
- **High Contrast**: Visible on light and dark backgrounds
- **Avoid Text**: Text doesn't scale well to small sizes
- **Brand Colors**: Use your application's color scheme

### Recommended Theme
For Smart Hiring System, consider:
- **Theme**: Technology, AI, People, Growth
- **Colors**: Purple/Blue gradient (matching the app)
- **Symbol**: Could incorporate:
  - Profile/person silhouette
  - Brain/AI elements
  - Checkmark/success indicator
  - Handshake/hiring symbol

## Quick Icon Generation

### Option 1: Use AI Image Generator
```
Prompt: "Modern minimalist app icon for AI recruitment software, 
purple and blue gradient, professional, simple geometric design, 
flat design style, no text"
```

### Option 2: Use Icon Libraries
- [Flaticon](https://www.flaticon.com/)
- [Icons8](https://icons8.com/)
- [FontAwesome](https://fontawesome.com/)
- [Material Design Icons](https://materialdesignicons.com/)

### Option 3: Hire a Designer
- Fiverr (budget-friendly)
- 99designs (competitive designs)
- Upwork (professional designers)

## Conversion Tools

### Online Converters
1. **PNG to ICO**: https://icoconvert.com/
2. **Image Resizer**: https://www.iloveimg.com/resize-image
3. **Background Remover**: https://www.remove.bg/

### Desktop Tools
1. **GIMP** (Free, open-source)
2. **Adobe Photoshop** (Professional)
3. **Inkscape** (Free, vector graphics)

## Filename Convention

Place files exactly as named:
```
desktop/assets/
├── icon.ico       # Windows icon (multi-resolution)
├── icon.png       # High-res PNG (512x512+)
└── logo.png       # Installer banner (164x314)
```

## Build Behavior

- **With Icons**: Uses your custom icons
- **Without Icons**: Uses electron-builder default icon (electron logo)
- **Missing ICO**: Build may fail on Windows
- **Missing PNG**: Some platforms may use default

## Testing Your Icons

After adding icons:

```powershell
# Rebuild the application
cd build_scripts
.\build_electron_app.ps1 -Clean

# Check the installer
cd ..\desktop\dist
.\Smart*.exe
```

Your custom icon should appear:
- During installation
- In Start Menu
- On Desktop shortcut
- In taskbar when running
- In system tray

## Current Status

⚠️ **Icons not yet created** - Using placeholder file

Next steps:
1. Create or commission custom icons
2. Add files to this directory
3. Rebuild application
4. Verify icons appear correctly
