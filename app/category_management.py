import json

class CategoryNode:
    def __init__(self, name):
        self.name = name
        self._children = []

    def children(self):
        return self._children

    def add_child(self, child_node):
        if isinstance(child_node, CategoryNode):
            self._children.append(child_node)
        else:
            raise ValueError("Child must be a CategoryNode object")

    def delete_child(self, child_name):
        for child in self._children:
            if child.name == child_name:
                self._children.remove(child)
                return True
        return False

    def __repr__(self):
        return f"CategoryNode({self.name})"

    def __str__(self):
        return self.name

class CategoryManager:
    def __init__(self, json_file_path):
        self.json_file_path = json_file_path
        self.root_categories = []
        self.raw_json = ""
        self.category_data = {}
        self.load_categories()

    def load_categories(self):
        with open(self.json_file_path, 'r') as file:
            #self.category_data = json.load(file)
            self.raw_json = file.read()
            category_data = json.loads(self.raw_json)
        
        self.root_categories = []
        for category_name, subcategories in self.category_data.items():
            root_category = CategoryNode(category_name)
            self._process_subcategories(root_category, subcategories)
            self.root_categories.append(root_category)

    def _process_subcategories(self, parent_node, subcategories):
        for subcategory_name, sub_subcategories in subcategories.items():
            subcategory_node = CategoryNode(subcategory_name)
            parent_node.add_child(subcategory_node)
            self._process_subcategories(subcategory_node, sub_subcategories)

    def print_categories(self, node=None, level=0):
        if node is None:
            for root_category in self.root_categories:
                self.print_categories(root_category, level)
        else:
            print("  " * level + f"- {node.name}")
            for child in node.children():
                self.print_categories(child, level + 1)
                
    def get_all_categories_str(self):
        def _build_category_str(node, level=0):
            result = "  " * level + f"- {node.name}\n"
            for child in node.children():
                result += _build_category_str(child, level + 1)
            return result

        return "".join(_build_category_str(root) for root in self.root_categories)

    def get_raw_json(self):
        return self.raw_json

# Usage example
if __name__ == "__main__":
    cat_man = CategoryManager("app/static/ref/categories.json")
    print("Category Hierarchy:")
    cat_man.print_categories()
