import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;
import 'package:flutter_frontend/static/constants.dart';

class EditPictureForm extends StatefulWidget {
  const EditPictureForm({Key? key}) : super(key: key);

  @override
  State<EditPictureForm> createState() => _EditPictureFormState();
}

class _EditPictureFormState extends State<EditPictureForm> {
  final _formKey = GlobalKey<FormState>();
  final storage = const FlutterSecureStorage();

  bool _loading = true;
  String? _error;
  String? _successMessage;

  final TextEditingController _titleController = TextEditingController();
  final TextEditingController _descriptionController = TextEditingController();

  List<TextEditingController> _tagControllers = [];
  List<TextEditingController> _peopleControllers = [];

  @override
  void initState() {
    super.initState();
    _fetchPicture();
  }

  @override
  void dispose() {
    _titleController.dispose();
    _descriptionController.dispose();
    for (final c in _tagControllers) {
      c.dispose();
    }
    for (final c in _peopleControllers) {
      c.dispose();
    }
    super.dispose();
  }

  Future<void> _fetchPicture() async {
    try {
      final token = await storage.read(key: 'token');
      final serial = await storage.read(key: 'editPictureSerial');

      if (token == null || serial == null) {
        throw Exception('Missing token or picture serial');
      }

      final response = await http.get(
        Uri.parse('$server/get/picture_record/$serial'),
        headers: {'Authorization': token, 'Content-Type': 'application/json'},
      );

      if (response.statusCode != 200) {
        throw Exception('Failed to fetch picture data');
      }

      final data = jsonDecode(response.body)['data'];

      setState(() {
        _titleController.text = data['picture_title'] ?? '';
        _descriptionController.text = data['picture_description'] ?? '';

        _tagControllers = (data['picture_tags'] ?? '')
            .toString()
            .split(',')
            .where((e) => e.isNotEmpty)
            .map((e) => TextEditingController(text: e))
            .toList();

        _peopleControllers = (data['picture_people'] ?? '')
            .toString()
            .split(',')
            .where((e) => e.isNotEmpty)
            .map((e) => TextEditingController(text: e))
            .toList();

        _loading = false;
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
        _loading = false;
      });
    }
  }

  Future<void> _submitForm() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() {
      _error = null;
      _successMessage = null;
    });

    try {
      final token = await storage.read(key: 'token');
      final serial = await storage.read(key: 'editPictureSerial');

      if (token == null || serial == null) {
        throw Exception('Missing token or picture serial');
      }

      final response = await http.patch(
        Uri.parse('$server/update/picture_record/$serial/'),
        headers: {'Authorization': token, 'Content-Type': 'application/json'},
        body: jsonEncode({
          'picture_title': _titleController.text,
          'picture_description': _descriptionController.text,
          'tags': _tagControllers.map((e) => e.text).join(','),
          'people': _peopleControllers.map((e) => e.text).join(','),
        }),
      );

      if (response.statusCode != 200) {
        throw Exception('Failed to update picture');
      }

      setState(() {
        _successMessage = 'Picture details updated successfully!';
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
      });
    }
  }

  Widget _buildDynamicList(
    String title,
    List<TextEditingController> controllers,
    VoidCallback onAdd,
    void Function(int) onRemove,
  ) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          title,
          style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 8),
        ...controllers.asMap().entries.map((entry) {
          final index = entry.key;
          final controller = entry.value;
          return Row(
            children: [
              Expanded(
                child: TextFormField(
                  controller: controller,
                  validator: (value) {
                    return null;
                  },
                ),
              ),
              IconButton(
                icon: const Icon(Icons.remove_circle),
                onPressed: () => setState(() => onRemove(index)),
              ),
            ],
          );
        }),
        TextButton.icon(
          onPressed: () => setState(onAdd),
          icon: const Icon(Icons.add),
          label: const Text('Add'),
        ),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return const Center(child: CircularProgressIndicator());
    }

    return Padding(
      padding: const EdgeInsets.all(16),
      child: Form(
        key: _formKey,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (_error != null)
              Text(_error!, style: const TextStyle(color: Colors.red)),

            if (_successMessage != null)
              Text(
                _successMessage!,
                style: const TextStyle(color: Colors.green),
              ),

            TextFormField(
              controller: _titleController,
              decoration: const InputDecoration(labelText: 'Title'),
              validator: (value) {
                if (value == null || value.trim().isEmpty) {
                  return 'Please enter a title';
                }
                return null;
              },
            ),

            TextFormField(
              controller: _descriptionController,
              decoration: const InputDecoration(labelText: 'Description'),
              validator: (value) {
                return null;
              },
            ),

            const SizedBox(height: 20),

            _buildDynamicList(
              'Tags',
              _tagControllers,
              () => _tagControllers.add(TextEditingController()),
              (i) => _tagControllers.removeAt(i),
            ),

            const SizedBox(height: 20),

            _buildDynamicList(
              'People',
              _peopleControllers,
              () => _peopleControllers.add(TextEditingController()),
              (i) => _peopleControllers.removeAt(i),
            ),

            const SizedBox(height: 30),

            ElevatedButton(
              onPressed: _submitForm,
              child: const Text('Save Changes'),
            ),
          ],
        ),
      ),
    );
  }
}
