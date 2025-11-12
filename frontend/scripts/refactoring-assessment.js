/**
 * Refactoring Quality Assessment Script
 * 
 * Analyzes codebase structure, complexity, and organization
 * to assess refactoring quality
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const srcDir = path.join(__dirname, '../src');

// Metrics to collect
const metrics = {
  totalFiles: 0,
  totalLines: 0,
  featureFiles: 0,
  sharedFiles: 0,
  componentFiles: 0,
  hookFiles: 0,
  apiFiles: 0,
  contextFiles: 0,
  typeFiles: 0,
  utilsFiles: 0,
  averageFileSize: 0,
  largestFiles: [],
  featureStructure: {},
  importAnalysis: {},
};

// File size limits (in lines)
const FILE_SIZE_LIMITS = {
  small: 100,
  medium: 300,
  large: 500,
  veryLarge: 1000,
};

function countLines(filePath) {
  try {
    const content = fs.readFileSync(filePath, 'utf-8');
    return content.split('\n').length;
  } catch (error) {
    return 0;
  }
}

function analyzeFile(filePath, relativePath) {
  const lines = countLines(filePath);
  const segments = relativePath.split(path.sep);
  
  metrics.totalFiles++;
  metrics.totalLines += lines;
  
  // Categorize by location
  if (segments[0] === 'features') {
    metrics.featureFiles++;
    const featureName = segments[1];
    if (!metrics.featureStructure[featureName]) {
      metrics.featureStructure[featureName] = { files: 0, lines: 0 };
    }
    metrics.featureStructure[featureName].files++;
    metrics.featureStructure[featureName].lines += lines;
  } else if (segments[0] === 'shared') {
    metrics.sharedFiles++;
  } else if (segments[0] === 'components') {
    metrics.componentFiles++;
  } else if (segments[0] === 'hooks') {
    metrics.hookFiles++;
  } else if (segments[0] === 'api') {
    metrics.apiFiles++;
  } else if (segments[0] === 'contexts') {
    metrics.contextFiles++;
  } else if (segments[0] === 'types') {
    metrics.typeFiles++;
  } else if (segments[0] === 'utils') {
    metrics.utilsFiles++;
  }
  
  // Track largest files
  if (lines > 200) {
    metrics.largestFiles.push({ path: relativePath, lines });
    metrics.largestFiles.sort((a, b) => b.lines - a.lines);
    if (metrics.largestFiles.length > 20) {
      metrics.largestFiles.pop();
    }
  }
}

function walkDirectory(dir, baseDir = dir) {
  const files = fs.readdirSync(dir);
  
  for (const file of files) {
    const filePath = path.join(dir, file);
    const stat = fs.statSync(filePath);
    
    if (stat.isDirectory()) {
      // Skip node_modules, dist, etc.
      if (!['node_modules', 'dist', '.git', 'coverage'].includes(file)) {
        walkDirectory(filePath, baseDir);
      }
    } else if (file.endsWith('.ts') || file.endsWith('.tsx')) {
      const relativePath = path.relative(baseDir, filePath);
      analyzeFile(filePath, relativePath);
    }
  }
}

function analyzeImports() {
  // Simple import analysis - count feature imports vs shared imports
  const featureImports = {};
  const sharedImports = {};
  
  function scanImports(filePath) {
    try {
      const content = fs.readFileSync(filePath, 'utf-8');
      const importRegex = /import\s+.*?\s+from\s+['"]([^'"]+)['"]/g;
      let match;
      
      while ((match = importRegex.exec(content)) !== null) {
        const importPath = match[1];
        if (importPath.startsWith('@/features/')) {
          const feature = importPath.split('/')[2];
          featureImports[feature] = (featureImports[feature] || 0) + 1;
        } else if (importPath.startsWith('@/shared/')) {
          const shared = importPath.split('/')[2];
          sharedImports[shared] = (sharedImports[shared] || 0) + 1;
        }
      }
    } catch (error) {
      // Ignore errors
    }
  }
  
  function walkForImports(dir) {
    const files = fs.readdirSync(dir);
    for (const file of files) {
      const filePath = path.join(dir, file);
      const stat = fs.statSync(filePath);
      
      if (stat.isDirectory()) {
        if (!['node_modules', 'dist', '.git', 'coverage'].includes(file)) {
          walkForImports(filePath);
        }
      } else if (file.endsWith('.ts') || file.endsWith('.tsx')) {
        scanImports(filePath);
      }
    }
  }
  
  walkForImports(srcDir);
  
  metrics.importAnalysis = {
    featureImports,
    sharedImports,
  };
}

function generateReport() {
  metrics.averageFileSize = Math.round(metrics.totalLines / metrics.totalFiles);
  
  const report = {
    summary: {
      totalFiles: metrics.totalFiles,
      totalLines: metrics.totalLines,
      averageFileSize: metrics.averageFileSize,
    },
    structure: {
      features: metrics.featureFiles,
      shared: metrics.sharedFiles,
      components: metrics.componentFiles,
      hooks: metrics.hookFiles,
      api: metrics.apiFiles,
      contexts: metrics.contextFiles,
      types: metrics.typeFiles,
      utils: metrics.utilsFiles,
    },
    featureBreakdown: metrics.featureStructure,
    largestFiles: metrics.largestFiles.slice(0, 10),
    importAnalysis: metrics.importAnalysis,
    assessment: {
      featureBasedStructure: metrics.featureFiles > 0,
      properSeparation: {
        features: metrics.featureFiles,
        shared: metrics.sharedFiles,
        components: metrics.componentFiles,
      },
      fileSizeHealth: {
        largeFiles: metrics.largestFiles.filter(f => f.lines > FILE_SIZE_LIMITS.large).length,
        veryLargeFiles: metrics.largestFiles.filter(f => f.lines > FILE_SIZE_LIMITS.veryLarge).length,
      },
    },
  };
  
  return report;
}

// Main execution
console.log('🔍 Analyzing refactoring quality...\n');
walkDirectory(srcDir);
analyzeImports();
const report = generateReport();

// Print report
console.log('📊 REFACTORING QUALITY ASSESSMENT\n');
console.log('='.repeat(60));
console.log('\n📈 SUMMARY');
console.log(`Total Files: ${report.summary.totalFiles}`);
console.log(`Total Lines: ${report.summary.totalLines.toLocaleString()}`);
console.log(`Average File Size: ${report.summary.averageFileSize} lines\n`);

console.log('📁 STRUCTURE BREAKDOWN');
console.log(`Features: ${report.structure.features} files`);
console.log(`Shared: ${report.structure.shared} files`);
console.log(`Components: ${report.structure.components} files`);
console.log(`Hooks: ${report.structure.hooks} files`);
console.log(`API: ${report.structure.api} files`);
console.log(`Contexts: ${report.structure.contexts} files`);
console.log(`Types: ${report.structure.types} files`);
console.log(`Utils: ${report.structure.utils} files\n`);

console.log('🎯 FEATURE BREAKDOWN');
Object.entries(report.featureBreakdown).forEach(([feature, data]) => {
  console.log(`  ${feature}: ${data.files} files, ${data.lines} lines`);
});
console.log('');

console.log('📦 LARGEST FILES (Top 10)');
report.largestFiles.forEach((file, index) => {
  const size = file.lines > FILE_SIZE_LIMITS.veryLarge ? '🔴' : 
               file.lines > FILE_SIZE_LIMITS.large ? '🟡' : '🟢';
  console.log(`  ${index + 1}. ${size} ${file.path} (${file.lines} lines)`);
});
console.log('');

console.log('✅ ASSESSMENT');
console.log(`Feature-based structure: ${report.assessment.featureBasedStructure ? '✅ Yes' : '❌ No'}`);
console.log(`Large files (>500 lines): ${report.assessment.fileSizeHealth.largeFiles}`);
console.log(`Very large files (>1000 lines): ${report.assessment.fileSizeHealth.veryLargeFiles}`);
console.log('');

// Save JSON report
const reportPath = path.join(__dirname, '../refactoring-assessment.json');
fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
console.log(`📄 Full report saved to: ${reportPath}`);

