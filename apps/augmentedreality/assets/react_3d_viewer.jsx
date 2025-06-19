import React from 'react'
import { createRoot } from 'react-dom/client'
import { widget as ReactWidget } from 'adhocracy4'
import * as OV from 'online-3d-viewer'

import { HashRouter } from 'react-router-dom'

function init () {
  ReactWidget.initialise('arpas', 'viewer',
    function (el) {
      const props = el.dataset.attributes ? JSON.parse(el.dataset.attributes) : {}
      const root = createRoot(el)
      OV.Init3DViewerElements();

      // TODO: Fetch model from MinIO and pass to model prop below
      root.render(
        <React.StrictMode>
          <HashRouter>
            <div>
                <h3>Beautiful 3d viewer </h3>
                    <div 
                        className="online_3d_viewer"
                        style={{width: '100%', height: '600px'}}
                        model="/static/images/tree.glb"
                        />
                </div>
          </HashRouter>
        </React.StrictMode>
      )
    }
  )
}

document.addEventListener('DOMContentLoaded', init, false)







