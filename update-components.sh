#!/bin/bash

# Script to update all components to use config.js

echo "🔄 Updating components to use config.js..."

# List of files to update
files=(
  "frontend/src/pages/Dashboard.jsx"
  "frontend/src/pages/DocumentAnalyzer.jsx"
  "frontend/src/pages/CompareReports.jsx"
  "frontend/src/pages/CompanyDetail.jsx"
  "frontend/src/components/CompanySearch.jsx"
)

for file in "${files[@]}"; do
  if [ -f "$file" ]; then
    echo "✅ Checking: $file"
    # Add import if not present
    if ! grep -q "import.*config" "$file"; then
      echo "⚠️  Needs manual update: $file"
    fi
  fi
done

echo "✨ Done! Please manually update the fetch() calls in each file."