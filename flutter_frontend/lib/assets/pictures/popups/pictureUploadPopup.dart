import 'dart:convert';
import 'dart:io' show File;
import 'dart:typed_data';

import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;
import 'package:image_picker/image_picker.dart';

import 'package:flutter_frontend/static/constants.dart';

import 'dart:html' as html;

class PictureUploadPopup extends StatefulWidget {
  const PictureUploadPopup({Key? key}) : super(key: key);

  @override
  State<PictureUploadPopup> createState() => _PictureUploadPopupState();
}

class _PictureUploadPopupState extends State<PictureUploadPopup> {
  final storage = const FlutterSecureStorage();
  final picker = ImagePicker();

  File? mobileImage;
  html.File? webImage;
  Uint8List? webImageBytes;

  String album = '';
  String title = '';
  String description = '';

  List<String> tags = [];
  List<String> people = [];

  bool userEditable = true;
  bool isUploading = false;
  String? error;

  final tagController = TextEditingController();
  final peopleController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _loadAlbum();
  }

  @override
  void dispose() {
    tagController.dispose();
    peopleController.dispose();
    super.dispose();
  }

  Future<void> _loadAlbum() async {
    final albumSerial = await storage.read(key: 'defaultAlbumSerial');
    if (albumSerial != null) {
      setState(() => album = albumSerial);
      await _loadAlbumMetadata(albumSerial);
    }
  }

  Future<void> _loadAlbumMetadata(String album) async {
    final token = await storage.read(key: 'token');

    try {
      final response = await http.get(
        Uri.parse('$server/get/tags/$album'),
        headers: {'Authorization': token ?? ''},
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        setState(() {
          tags = List<String>.from(data['tags'] ?? []);
          people = List<String>.from(data['people'] ?? []);
        });
      } else {
        setState(() => error = 'Failed to load album metadata');
      }
    } catch (e) {
      setState(() => error = e.toString());
    }
  }

  Future<void> _pickImage() async {
    if (kIsWeb) {
      final input = html.FileUploadInputElement()..accept = 'image/*';
      input.click();

      input.onChange.listen((_) {
        final file = input.files?.first;
        if (file != null) {
          final reader = html.FileReader();

          reader.readAsArrayBuffer(file);

          reader.onLoadEnd.listen((_) {
            setState(() {
              webImage = file;
              webImageBytes = reader.result as Uint8List;
            });
          });
        }
      });
    } else {
      final picked = await picker.pickImage(source: ImageSource.gallery);
      if (picked != null) {
        setState(() => mobileImage = File(picked.path));
      }
    }
  }

  Future<void> _uploadPicture() async {
    if ((kIsWeb && webImageBytes == null) || (!kIsWeb && mobileImage == null)) {
      setState(() => error = 'Please select an image');
      return;
    }

    setState(() {
      isUploading = true;
      error = null;
    });

    try {
      final token = await storage.read(key: 'token');

      final request = http.MultipartRequest(
        'POST',
        Uri.parse('$server/upload/picture/'),
      );

      request.headers['Authorization'] = token ?? '';

      request.fields.addAll({
        'album': album,
        'title': title,
        'description': description,
        'tags': tags.join(','),
        'people': people.join(','),
        'user_editable': userEditable.toString(),
      });

      if (kIsWeb) {
        request.files.add(
          http.MultipartFile.fromBytes(
            'image',
            webImageBytes!,
            filename: webImage!.name,
          ),
        );
      } else {
        request.files.add(
          await http.MultipartFile.fromPath('image', mobileImage!.path),
        );
      }

      final response = await request.send();

      if (response.statusCode == 201) {
        Navigator.of(context).pop(true);
      } else {
        setState(() => error = 'Upload failed');
      }
    } catch (e) {
      setState(() => error = e.toString());
    } finally {
      setState(() => isUploading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text('Upload Picture'),
      content: SingleChildScrollView(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            ElevatedButton(
              onPressed: _pickImage,
              child: const Text('Select Image'),
            ),

            if (kIsWeb && webImage != null)
              Padding(
                padding: const EdgeInsets.only(top: 8),
                child: Text(webImage!.name),
              ),

            if (!kIsWeb && mobileImage != null)
              Padding(
                padding: const EdgeInsets.only(top: 8),
                child: Text(mobileImage!.path.split('/').last),
              ),

            const SizedBox(height: 12),

            TextField(
              controller: TextEditingController(text: album),
              enabled: false,
              decoration: const InputDecoration(labelText: 'Album'),
            ),

            TextField(
              decoration: const InputDecoration(labelText: 'Title'),
              onChanged: (v) => title = v,
            ),

            TextField(
              decoration: const InputDecoration(labelText: 'Description'),
              maxLines: 3,
              onChanged: (v) => description = v,
            ),

            const SizedBox(height: 8),

            TextField(
              controller: tagController,
              decoration: const InputDecoration(
                labelText: 'Tags',
                hintText: 'Press Enter to add',
              ),
              onSubmitted: (v) {
                if (v.trim().isNotEmpty) {
                  setState(() {
                    tags.add(v.trim());
                    tagController.clear();
                  });
                }
              },
            ),

            Wrap(
              spacing: 6,
              children: tags
                  .map(
                    (t) => Chip(
                      label: Text(t),
                      onDeleted: () => setState(() => tags.remove(t)),
                    ),
                  )
                  .toList(),
            ),

            const SizedBox(height: 8),

            TextField(
              controller: peopleController,
              decoration: const InputDecoration(
                labelText: 'People',
                hintText: 'Press Enter to add',
              ),
              onSubmitted: (v) {
                if (v.trim().isNotEmpty) {
                  setState(() {
                    people.add(v.trim());
                    peopleController.clear();
                  });
                }
              },
            ),

            Wrap(
              spacing: 6,
              children: people
                  .map(
                    (p) => Chip(
                      label: Text(p),
                      onDeleted: () => setState(() => people.remove(p)),
                    ),
                  )
                  .toList(),
            ),

            CheckboxListTile(
              value: userEditable,
              onChanged: (v) => setState(() => userEditable = v ?? true),
              title: const Text('User Editable'),
              controlAffinity: ListTileControlAffinity.leading,
            ),

            if (error != null)
              Padding(
                padding: const EdgeInsets.only(top: 8),
                child: Text(error!, style: const TextStyle(color: Colors.red)),
              ),
          ],
        ),
      ),
      actions: [
        TextButton(
          onPressed: isUploading ? null : () => Navigator.pop(context),
          child: const Text('Cancel'),
        ),
        ElevatedButton(
          onPressed: isUploading ? null : _uploadPicture,
          child: isUploading
              ? const SizedBox(
                  width: 16,
                  height: 16,
                  child: CircularProgressIndicator(strokeWidth: 2),
                )
              : const Text('Upload'),
        ),
      ],
    );
  }
}
