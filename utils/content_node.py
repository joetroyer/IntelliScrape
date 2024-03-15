import re

class ContentNode:
    def __init__(self, tag=None, id=None, classes=None):
        self.tag = tag
        self.id = self.escape_css_identifier(id) if id else None
        self.classes = [self.escape_css_identifier(cls) for cls in classes] if classes else []
        self.content = []
        self.children = []

    # Define the truncate_text function
    def truncate_text(self, text, max_length=70):
        return text[:max_length] + '...' if len(text) > max_length else text

    def add_content(self, text):
        truncated_text = self.truncate_text(text)
        self.content.append(truncated_text)

    def add_child(self, child_node):
        self.children.append(child_node)

    def escape_css_identifier(self, identifier):
        # Escape special characters with a backslash
        return re.sub(r'([!"#$%&\'()*+,./:;<=>?@[\\]^`{|}~])', r'\\\1', identifier)

    def get_text(self):
        return ' '.join(self.content)
