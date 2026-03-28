import re

def update_css(content):
    # Update roots
    new_root = """:root {
  /* Neon Observatory Tokens */
  --primary: #f3fff3;
  --primary_container: #00ff9c;
  --on_primary: #00391f;
  --primary_fixed: #56ffa7;
  --primary_fixed_dim: #00e38a;
  --secondary: #5bd5fc;
  --secondary_container: #00a3c8;
  --secondary_fixed: #b7eaff;
  --tertiary: #fffaff;
  --on_tertiary_container: #c01943;
  --outline: #849587;
  --outline_variant: #3b4b3f;
  
  --surface: #101419;
  --surface_dim: #0B0F14;
  --surface_variant: #31353b;
  --surface_container_high: #262a30;
  
  --on_surface: #e0e2ea;
  --on_surface_variant: #b9cbbc;

  --bg-dark: var(--surface);
  --bg-card: rgba(255,255,255,0.05); /* 5% opacity for glass */
  --bg-card-hover: rgba(255,255,255,0.08);
  --border-ghost: rgba(59,75,63,0.15); /* outline_variant at 15% */
  
  --text-1: var(--on_surface);
  --text-2: var(--primary);
  --text-3: var(--on_surface_variant);

  /* Legacy variable mappings to ease transition */
  --green-400: var(--primary_container);
  --green-500: var(--primary_fixed_dim);
  --green-600: var(--on_primary);
  --green-900: #002110;
  --amber-400: #fbbf24;
  --amber-500: #f59e0b;
  --red-400: #ffb4ab;
  --red-500: #93000a;
  --blue-400: var(--secondary);

  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 24px;
  --radius-xl: 32px;

  --font-body: 'Inter', sans-serif;
  --font-head: 'Space Grotesk', sans-serif;

  --transition: 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}"""
    content = re.sub(r':root\s*\{.*?(?=body \{)', new_root + "\n\nhtml { scroll-behavior: smooth; }\n\n", content, flags=re.DOTALL)
    
    # Update body background
    content = content.replace("background: var(--bg-dark);", "background: linear-gradient(135deg, var(--surface) 0%, var(--surface_dim) 100%);")
    
    # Replace glass card
    glass = """.glass-card {
  background: var(--bg-card);
  border: 1px solid var(--border-ghost);
  border-radius: var(--radius-lg);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  transition: box-shadow var(--transition), border-color var(--transition);
}
.glass-card:hover {
  border-color: rgba(91, 213, 252, 0.15);
  box-shadow: 0 0 32px rgba(91, 213, 252, 0.04);
}"""
    content = re.sub(r'\.glass-card\s*\{[^}]*\}[^{]*\.glass-card:hover\s*\{[^}]*\}', glass, content)
    
    # Update buttons
    content = content.replace("box-shadow: 0 4px 20px rgba(34,197,94,0.35);", "box-shadow: none;")
    content = content.replace("box-shadow: 0 8px 32px rgba(34,197,94,0.5);", "box-shadow: 0 0 20px rgba(86, 255, 167, 0.4);")
    content = content.replace("background: linear-gradient(135deg, var(--green-500), var(--green-600));\n  color: #fff;", "background: var(--primary_container);\n  color: var(--on_primary);")
    content = content.replace("border: 1px solid var(--border);", "border: 1px solid var(--border-ghost);")
    content = content.replace("border-color: var(--green-400);", "border-color: var(--outline);")
    content = content.replace("background: rgba(74,222,128,0.05);", "background: rgba(0, 255, 156, 0.05);")
    content = content.replace("background: rgba(74,222,128,0.08);", "background: rgba(0, 255, 156, 0.08);")
    content = content.replace("border: 1px solid rgba(74,222,128,0.4);", "border: 1px solid var(--border-ghost);")

    # Hero Gradient
    content = content.replace("background: linear-gradient(135deg, var(--green-400) 0%, var(--amber-400) 100%);", "background: linear-gradient(135deg, var(--primary_container) 0%, var(--secondary) 100%);")

    # Fix specific RGBAs (e.g. 74,222,128 for --green-400 and #4ade80, #16a34a)
    content = content.replace("rgba(74,222,128,", "rgba(0, 255, 156,")
    content = content.replace("rgba(34,197,94,", "rgba(0, 227, 138,")
    
    return content

def update_html(content):
    content = content.replace("#4ade80", "#00ff9c")
    content = content.replace("#16a34a", "#00391f")
    content = content.replace("#22c55e", "#00e38a")
    return content

def update_js(content):
    content = content.replace("#4ade80", "#00ff9c")
    content = content.replace("#16a34a", "#00391f") 
    content = content.replace("#22c55e", "#00e38a")
    return content

import os
base_path = r"c:\Users\KIIT0001\Desktop\smart-crop-health-main\frontend"

for f, func in [("styles.css", update_css), ("index.html", update_html), ("app.js", update_js)]:
    with open(os.path.join(base_path, f), "r", encoding="utf-8") as file:
        data = file.read()
    data = func(data)
    with open(os.path.join(base_path, f), "w", encoding="utf-8") as file:
        file.write(data)

print("Files updated")
