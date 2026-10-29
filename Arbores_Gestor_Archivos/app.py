from flask import Flask, jsonify, render_template, request
from src.services.file_service import FileService
from src.structures.nary_tree import TreeError

def create_app(data_path=None):
    app = Flask(__name__)
    service = FileService(data_path=data_path)

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.get("/api/tree")
    def get_tree():
        return jsonify(service.get_tree_data())

    @app.get("/api/stats")
    def get_stats():
        return jsonify(service.get_stats())

    @app.get("/api/node/<node_id>")
    def get_node(node_id):
        node = service.tree.find_by_id(node_id)
        if node is None:
            return jsonify({"error": "No se encontró el elemento."}), 404
        return jsonify(service.node_details(node))

    @app.post("/api/nodes")
    def create_node():
        payload = request.get_json(silent=True) or {}
        try:
            node = service.create_node(
                parent_id=payload.get("parent_id"),
                name=payload.get("name", ""),
                node_type=payload.get("type", "")
            )
            return jsonify({"message": "Elemento creado correctamente.", "node": service.node_details(node)}), 201
        except (TreeError, ValueError) as error:
            return jsonify({"error": str(error)}), 400

    @app.patch("/api/nodes/<node_id>")
    def rename_node(node_id):
        payload = request.get_json(silent=True) or {}
        try:
            node = service.rename_node(node_id, payload.get("name", ""))
            return jsonify({"message": "Elemento renombrado correctamente.", "node": service.node_details(node)})
        except (TreeError, ValueError) as error:
            return jsonify({"error": str(error)}), 400

    @app.delete("/api/nodes/<node_id>")
    def delete_node(node_id):
        try:
            service.delete_node(node_id)
            return jsonify({"message": "Elemento eliminado correctamente."})
        except (TreeError, ValueError) as error:
            return jsonify({"error": str(error)}), 400

    @app.post("/api/nodes/<node_id>/move")
    def move_node(node_id):
        payload = request.get_json(silent=True) or {}
        try:
            service.move_node(node_id, payload.get("parent_id"))
            return jsonify({"message": "Elemento movido correctamente."})
        except (TreeError, ValueError) as error:
            return jsonify({"error": str(error)}), 400

    @app.get("/api/search")
    def search_nodes():
        query = request.args.get("q", "")
        return jsonify(service.search(query))

    @app.get("/api/traversal/<method>")
    def traversal(method):
        try:
            return jsonify({"method": method.upper(), "items": service.traversal(method)})
        except ValueError as error:
            return jsonify({"error": str(error)}), 400

    @app.post("/api/reset")
    def reset():
        service.reset_demo()
        return jsonify({"message": "Se restauraron los datos de demostración.", "tree": service.get_tree_data()})

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
