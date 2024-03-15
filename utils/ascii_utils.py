from utils.content_node import ContentNode
import bs4

def generate_ascii_tree(node, prefix=""):
    lines = []

    # Add the current node tag
    node_repr = f"{node.tag}"
    if node.id:
        node_repr += f"#{node.id}"
    if node.classes:
        node_repr += f".{'.'.join(node.classes)}"
    if node.content:
        content_str = ' '.join(node.content)
        node_repr += f" - {content_str}"

    lines.append(prefix + node_repr)

    # Process children with recursion
    children_prefix = prefix + "│   "
    last_child_prefix = prefix + "    "
    for i, child in enumerate(node.children):
        is_last = i == (len(node.children) - 1)
        child_lines = generate_ascii_tree(child, children_prefix if not is_last else last_child_prefix)
        if is_last:
            child_lines[0] = prefix + "└── " + child_lines[0][len(prefix):]
        else:
            child_lines[0] = prefix + "├── " + child_lines[0][len(prefix):]
        lines.extend(child_lines)

    return lines

# Function to get the ASCII tree as a string
def get_ascii_tree_string(root_node):
    lines = generate_ascii_tree(root_node)
    return "\n".join(lines)

# Modify the process_tag function to work with ContentNode
def process_tag(tag, parent_node):
    # Create a ContentNode with the tag's name, id, and classes
    node = ContentNode(tag.name, tag.get('id'), tag.get('class'))
    text = tag.get_text(strip=True)
    if text:
        node.add_content(text)
    for child in tag.children:
        if isinstance(child, bs4.element.Tag):
            child_node = process_tag(child, node)
            node.add_child(child_node)
    return node

# The summarize_body function using ContentNode
def summarize_body_using_ascii_tree(soup):
    # Decompose unwanted tags
    for tag in soup(['script', 'style', 'meta', 'link', 'comment', 'head', 'footer', 'nav', 'form', 'noscript']):
        tag.decompose()

    # Start processing from the body tag or the root of the soup
    root_node = process_tag(soup.body if soup.body else soup, None)
    # Convert the tree of ContentNodes to a nested dictionary
    # summarized_dict = convert_to_dict(root_node)
    summarized_dict = get_ascii_tree_string(root_node=root_node)
    with open('tst.txt','w', encoding='utf-8') as f:
        f.write(summarized_dict)
    return summarized_dict
