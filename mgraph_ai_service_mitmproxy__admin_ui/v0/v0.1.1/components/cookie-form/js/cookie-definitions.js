// Cookie Definitions
// Configuration for all available proxy cookies
// Update this file to add/modify cookie options

const COOKIE_DEFINITIONS = [
    {
        name: 'mitm-show',
        description: 'Control content display',
        type: 'select',
        options: [ { value: 'url-to-html-xxx'   , label: 'URL to Html XXX'         },
                   { value: 'url-to-html-hashes', label: 'URL to Html Hashes'      },
                   { value: 'url-to-html-dict'  , label: 'URL to Html Dict (json)' },
                   { value: 'url-to-ratings'    , label: 'URL to Ratings'          },
                   { value: 'response-data'     , label: 'Response Data (json)'    }]
    },
    {
        name: 'mitm-inject',
        description: 'Inject debug content',
        type: 'select',
        options: [
            { value: 'debug-panel', label: 'Debug Panel' },
            { value: 'debug-banner', label: 'Debug Banner' }
        ]
    },
    {
        name: 'mitm-replace',
        description: 'Replace text (format: old:new)',
        type: 'text',
        placeholder: 'oldtext:newtext'
    },
    {
        name: 'mitm-debug',
        description: 'Enable debug mode',
        type: 'select',
        options: [
            { value: 'true', label: 'Enabled (true)' },
            { value: 'false', label: 'Disabled (false)' }
        ]
    },
    {
        name: 'mitm-rating',
        description: 'Set minimum rating threshold',
        type: 'number',
        placeholder: '0.5',
        min: '0',
        max: '1',
        step: '0.1'
    },
    {
        name: 'mitm-model',
        description: 'Override WCF model',
        type: 'text',
        placeholder: 'google/gemini-2.0-flash-lite-001'
    },
    {
        name: 'mitm-cache',
        description: 'Enable response caching',
        type: 'select',
        options: [
            { value: 'true', label: 'Enabled (true)' },
            { value: 'false', label: 'Disabled (false)' }
        ]
    }
];
