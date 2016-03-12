# coding: utf-8
"""
created by artemkorkhov at 2016/03/11
"""

import logging.config


logging.config.dictConfig({
    'version': 1,
    'formatters': {
        'simple': {
            'format': '%(asctime)s\t%(name)s\t%(message)s'
        }
    },
    'handlers': {
        'console': {
            'class' : 'logging.StreamHandler',
            'formatter': 'simple',
            'level': 'DEBUG'
        },
        'file': {
            'class': 'logging.FileHandler',
            'formatter': 'simple',
            'level': 'DEBUG',
            'filename': 'ym.log',
            'mode': 'a'
        }
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'DEBUG'
    },
    'loggers': {
        '__main__': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': True
        },
    }
})
