# ♿ Accessibility Guide - Smart Hiring System

## Overview

This guide documents accessibility implementation for WCAG 2.1 Level AA compliance.

**Standards:** WCAG 2.1 Level AA, Section 508, ADA Compliance  
**Testing Tool:** axe-core  
**Target:** 100% keyboard navigable, screen reader compatible

---

## 🎯 Accessibility Features Implemented

### 1. Keyboard Navigation
- **Tab Navigation:** All interactive elements reachable via Tab
- **Arrow Keys:** Navigate lists, menus, and radio groups
- **Enter/Space:** Activate buttons and links
- **Escape:** Close modals, dropdowns, and overlays
- **Global Shortcuts:**
  - `Ctrl/Cmd + /` → Show keyboard shortcuts
  - `Ctrl/Cmd + K` → Focus search
  - `Home/End` → Jump to first/last item in lists

### 2. Focus Management
- **Visible Focus Indicators:** 3px solid outline with 2px offset
- **Focus Trapping:** Modals trap focus within dialog
- **Focus Restoration:** Previous focus restored when modal closes
- **Skip Links:** "Skip to main content" for screen readers

### 3. Screen Reader Support
- **ARIA Labels:** All interactive elements labeled
- **Live Regions:** Dynamic content announcements
- **Semantic HTML:** Proper heading hierarchy (h1-h6)
- **Alt Text:** All images have descriptive alt attributes
- **Form Labels:** All inputs properly labeled with `<label>` or `aria-label`

### 4. Color Contrast
- **Normal Text:** 4.5:1 contrast ratio (WCAG AA)
- **Large Text:** 3:1 contrast ratio (WCAG AA)
- **Interactive Elements:** 3:1 contrast with surroundings
- **Error States:** High contrast red (#dc2626) with 5.4:1 ratio
- **Success States:** High contrast green (#047857) with 4.7:1 ratio

### 5. Responsive & Mobile
- **Touch Targets:** Minimum 44x44px (WCAG Level AAA)
- **Pinch Zoom:** Enabled (no `maximum-scale=1`)
- **Orientation:** Works in both portrait and landscape
- **Mobile Navigation:** Accessible hamburger menu

### 6. Motion & Animation
- **Reduced Motion:** Respects `prefers-reduced-motion` setting
- **Animations:** Can be disabled via system preferences
- **Smooth Scroll:** Disabled for users with motion sensitivity

---

## 📋 Accessibility Audit Tool

### Running the Audit

1. Open `frontend/accessibility-audit.html` in browser
2. Click "Run Accessibility Audit"
3. Review violations by severity:
   - 🔴 **Critical** - Fix immediately
   - 🟠 **Serious** - Fix before release
   - 🔵 **Moderate** - Fix soon
   - 🟢 **Minor** - Fix when possible

### Automated Testing (CI/CD)

```bash
# Install axe-core
npm install --save-dev axe-core @axe-core/cli

# Run in CI pipeline
npx axe http://localhost:5000 --tags wcag2a,wcag2aa --exit
```

---

## 🛠️ Implementation Guide

### Adding Accessibility to New Components

#### 1. Buttons

```html
<!-- ✅ Good -->
<button 
    type="button" 
    aria-label="Close dialog"
    onclick="closeDialog()">
    ✕
</button>

<!-- ❌ Bad -->
<div onclick="closeDialog()">✕</div>
```

#### 2. Forms

```html
<!-- ✅ Good -->
<label for="email">Email Address <span class="required">*</span></label>
<input 
    type="email" 
    id="email" 
    name="email"
    required
    aria-required="true"
    aria-invalid="false"
    aria-describedby="email-error">
<span id="email-error" class="field-error" role="alert">
    Invalid email format
</span>

<!-- ❌ Bad -->
<input type="email" placeholder="Email">
```

#### 3. Modals

```html
<!-- ✅ Good -->
<div 
    class="modal" 
    role="dialog" 
    aria-labelledby="dialog-title"
    aria-describedby="dialog-description"
    aria-modal="true">
    <div class="modal-content">
        <h2 id="dialog-title">Confirm Action</h2>
        <p id="dialog-description">Are you sure?</p>
        <button onclick="confirm()">Yes</button>
        <button onclick="cancel()">Cancel</button>
    </div>
</div>
```

#### 4. Loading States

```html
<!-- ✅ Good -->
<div role="status" aria-live="polite" aria-busy="true">
    <span class="sr-only">Loading content...</span>
    <div class="spinner" aria-hidden="true"></div>
</div>

<!-- ❌ Bad -->
<div><div class="spinner"></div></div>
```

#### 5. Tables

```html
<!-- ✅ Good -->
<table role="table" aria-label="Job applications">
    <caption>List of job applications</caption>
    <thead>
        <tr>
            <th scope="col">Candidate</th>
            <th scope="col">Status</th>
            <th scope="col">Actions</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>John Doe</td>
            <td>Under Review</td>
            <td>
                <button aria-label="View John Doe's application">View</button>
            </td>
        </tr>
    </tbody>
</table>
```

---

## 🧪 Testing Checklist

### Manual Testing

#### Keyboard Navigation
- [ ] All links accessible via Tab
- [ ] All buttons accessible via Tab
- [ ] Forms can be completed with keyboard only
- [ ] Modals can be closed with Escape
- [ ] Dropdowns navigable with Arrow keys
- [ ] Focus never trapped unintentionally
- [ ] Tab order is logical

#### Screen Reader Testing (NVDA/JAWS/VoiceOver)
- [ ] All images have alt text
- [ ] Form labels announced correctly
- [ ] Error messages announced
- [ ] Dynamic content changes announced
- [ ] Buttons announce their purpose
- [ ] Headings read in order
- [ ] Links announce destination

#### Visual Testing
- [ ] Focus indicators visible (3px outline)
- [ ] Text contrast ≥ 4.5:1
- [ ] Color not sole means of info
- [ ] Text resizable to 200% without loss
- [ ] Works at 400% zoom
- [ ] No horizontal scrolling at mobile widths

#### Touch/Mobile Testing
- [ ] Touch targets ≥ 44x44px
- [ ] Pinch zoom enabled
- [ ] Works in both orientations
- [ ] No hover-only functionality

---

## 🔧 Accessibility Utilities

### JavaScript Helpers

```javascript
// Announce to screen readers
a11y.announce('Form submitted successfully', 'polite');

// Announce urgent messages
a11y.announce('Error: Invalid email', 'assertive');

// Focus management
a11y.setFocusTo('#error-summary');
a11y.focusFirstError();

// ARIA helpers
a11y.setAriaExpanded(button, true);
a11y.setAriaInvalid(input, true);
a11y.setAriaDescribedBy(input, 'error-message-id');

// Loading states
a11y.announceLoadingStart('Fetching jobs...');
a11y.announceLoadingComplete('Jobs loaded');

// Form validation
a11y.announceFormError('Email', 'Invalid format');
a11y.announceFormSuccess('Profile updated');
```

### CSS Classes

```css
/* Hide visually, keep for screen readers */
.sr-only { /* ... */ }

/* Show on keyboard focus */
.sr-only-focusable:focus { /* ... */ }

/* Skip link */
.skip-link { /* ... */ }

/* Required field indicator */
.required::after { content: ' *'; }
```

---

## 📊 WCAG 2.1 Compliance Status

### Level A (Must Have) ✅
- [x] 1.1.1 Non-text Content
- [x] 1.3.1 Info and Relationships
- [x] 2.1.1 Keyboard
- [x] 2.4.1 Bypass Blocks
- [x] 3.1.1 Language of Page
- [x] 4.1.1 Parsing
- [x] 4.1.2 Name, Role, Value

### Level AA (Should Have) ✅
- [x] 1.4.3 Contrast (Minimum)
- [x] 1.4.5 Images of Text
- [x] 2.4.6 Headings and Labels
- [x] 2.4.7 Focus Visible
- [x] 3.2.3 Consistent Navigation
- [x] 3.3.3 Error Suggestion
- [x] 3.3.4 Error Prevention

### Level AAA (Nice to Have) 🔄
- [x] 2.4.8 Location (breadcrumbs)
- [x] 2.5.5 Target Size (44x44px)
- [ ] 1.4.6 Contrast (Enhanced 7:1)
- [ ] 2.4.9 Link Purpose

---

## 🐛 Common Issues & Fixes

### Issue 1: Missing Form Labels
```html
<!-- ❌ Bad -->
<input type="text" placeholder="Name">

<!-- ✅ Fix -->
<label for="name">Name</label>
<input type="text" id="name" name="name">
```

### Issue 2: Poor Color Contrast
```css
/* ❌ Bad (3:1 ratio) */
color: #999999;

/* ✅ Fix (4.5:1 ratio) */
color: #666666;
```

### Issue 3: Non-Accessible Icons
```html
<!-- ❌ Bad -->
<button><i class="icon-close"></i></button>

/* ✅ Fix */
<button aria-label="Close dialog">
    <i class="icon-close" aria-hidden="true"></i>
</button>
```

### Issue 4: Keyboard Trap
```javascript
// ❌ Bad - no way to exit
modal.addEventListener('keydown', e => e.preventDefault());

// ✅ Fix - escape key closes
modal.addEventListener('keydown', e => {
    if (e.key === 'Escape') closeModal();
});
```

---

## 📚 Resources

### Testing Tools
- **axe DevTools:** Browser extension
- **WAVE:** Web accessibility evaluation tool
- **Lighthouse:** Chrome DevTools
- **NVDA:** Free screen reader (Windows)
- **VoiceOver:** Built-in screen reader (Mac)

### Documentation
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [ARIA Authoring Practices](https://www.w3.org/WAI/ARIA/apg/)
- [WebAIM](https://webaim.org/)
- [Deque University](https://dequeuniversity.com/)

### Internal Files
- `frontend/a11y.css` - Accessibility styles
- `frontend/a11y.js` - Accessibility utilities
- `frontend/accessibility-audit.html` - Audit tool

---

## 🆘 Support

**Questions?** Contact accessibility team or open an issue.

**Report Accessibility Issues:** accessibility@smarthiring.com

---

**Last Updated:** December 2025  
**Maintained By:** Frontend Team  
**Compliance Level:** WCAG 2.1 Level AA
