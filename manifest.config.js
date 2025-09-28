import { defineManifest } from '@crxjs/vite-plugin'
import pkg from './package.json'

export default defineManifest({
  manifest_version: 3,
  name: 'TruthMeter',
  version: pkg.version,
  icons: {
    48: 'public/logo.png',
  },
  background: {
    service_worker: "src/background.js",
  },
  permissions: [
    'sidePanel',
    'contentSettings',
    'tabs',
    'activeTab',
    'scripting',
  ],
  action: {
    default_title: 'Open Side Panel'
  },
  content_scripts: [{
    js: ['src/content/main.jsx'],
    matches: ['https://*/*'],
  }],
  side_panel: {
    default_path: 'src/sidepanel/index.html',
  },
})
