# Modern Dark Theme Robotics Laboratory Application Styles
HOME_STYLE = """
    background-color: #0a0e17;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #0a0e17, stop:1 #1c2526);
"""

HEADER_LABEL_STYLE = """
    color: #e0e6f0;
    font-size: 32px;
    font-weight: 600;
    font-family: 'Inter', sans-serif;
    letter-spacing: 1px;
    padding: 10px;
"""

BUTTON_STYLE = """
    QPushButton {
        background-color: #2a3441;
        color: #b0c4de;
        font-size: 20px;
        font-weight: 500;
        font-family: 'Roboto', sans-serif;
        padding: 18px;
        border: 1px solid #4a5a73;
        border-radius: 8px;
        min-height: 120px;
        min-width: 240px;
    }
"""

BUTTON_HOVER_STYLE = """
    QPushButton:hover {
        background-color: #3b4a5e;
        color: #ffffff;
        border: 1px solid #6b829b;
    }
    QPushButton:checked {
        background-color: #4a5a73;
        color: #e0e6f0;
        border: 1px solid #81a1c1;
    }
"""

RUN_BUTTON_STYLE = """
    QPushButton {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #5e81ac, stop:1 #81a1c1);
        color: #ffffff;
        font-size: 18px;
        font-weight: 600;
        font-family: 'Roboto', sans-serif;
        padding: 14px 30px;
        border: none;
        border-radius: 6px;
    }
    QPushButton:hover {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #81a1c1, stop:1 #a3bffa);
    }
"""

GRID_LAYOUT_CONFIG = {
    "rows": 2,
    "cols": 3,
    "spacing": 30,
    "margin": 20
}