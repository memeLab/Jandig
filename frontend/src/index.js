import React from 'react'
import { createRoot } from 'react-dom/client'

import { ArViewer } from './ar_viewer/ArViewer';

const root = createRoot(document.getElementById('root'));
root.render(<ArViewer exhibitUrl="http://localhost:8000/api/v1/exhibits/1/"></ArViewer>);
