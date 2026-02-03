import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:flutter_frontend/static/constants.dart';
import 'package:flutter_frontend/pages/management/editPicturePage.dart';

class DefaultImagePopup extends StatefulWidget {
  final Map<String, dynamic> image;
  final VoidCallback closePopup;
  final VoidCallback onNext;
  final VoidCallback onPrevious;
  final bool hasNext;
  final bool hasPrevious;

  const DefaultImagePopup({
    Key? key,
    required this.image,
    required this.closePopup,
    required this.onNext,
    required this.onPrevious,
    required this.hasNext,
    required this.hasPrevious,
  }) : super(key: key);

  @override
  State<DefaultImagePopup> createState() => _DefaultImagePopupState();
}

class _DefaultImagePopupState extends State<DefaultImagePopup> {
  final storage = const FlutterSecureStorage();
  Map<String, dynamic>? imageData;
  String? error;
  OverlayEntry? _submenuOverlay;

  @override
  void initState() {
    super.initState();
    _fetchImageData();
  }

  Future<void> _fetchImageData() async {
    try {
      final token = await storage.read(key: 'token') ?? '';
      final serial = widget.image['picture_serial'];

      final dataRes = await http.get(
        Uri.parse('$server/get/picture_data/$serial/'),
        headers: {'Authorization': token},
      );

      if (dataRes.statusCode != 200) {
        throw Exception('Failed to fetch image data');
      }

      final decoded = jsonDecode(dataRes.body);

      final imageRes = await http.get(
        Uri.parse('$server/get/picture_image/$serial/'),
        headers: {'Authorization': token},
      );

      if (imageRes.statusCode != 200) {
        throw Exception('Failed to fetch image');
      }

      setState(() {
        imageData = {
          ...decoded['data'],
          'imageUrl': base64Encode(imageRes.bodyBytes),
        };
      });
    } catch (e) {
      setState(() => error = e.toString());
    }
  }

  Future<void> _toggleFavourite() async {
    final token = await storage.read(key: 'token') ?? '';
    final serial = widget.image['picture_serial'];
    final action = imageData!['is_favourite'] ? 'remove' : 'add';

    final res = await http.post(
      Uri.parse('$server/update/image_favourites/$serial/'),
      headers: {'Authorization': token, 'Content-Type': 'application/json'},
      body: jsonEncode({'action': action}),
    );

    if (res.statusCode == 200) {
      setState(() {
        imageData!['is_favourite'] = !imageData!['is_favourite'];
      });
    }
  }

  Future<void> _addToAlbum(String albumSerial) async {
    final token = await storage.read(key: 'token') ?? '';
    final serial = widget.image['picture_serial'];

    await http.post(
      Uri.parse('$server/add/image/custom_album/$albumSerial/$serial/'),
      headers: {'Authorization': token},
    );
  }

  Future<void> _removeFromAlbum(String albumSerial) async {
    final token = await storage.read(key: 'token') ?? '';
    final serial = widget.image['picture_serial'];

    await http.delete(
      Uri.parse('$server/delete/image/custom_album/$albumSerial/$serial/'),
      headers: {'Authorization': token},
    );
  }

  Future<void> _editPicture() async {
    final serial = widget.image['picture_serial'];

    await storage.write(key: 'editPictureSerial', value: serial.toString());

    Navigator.of(
      context,
    ).push(MaterialPageRoute(builder: (_) => EditPicturePage()));
  }

  void _showSubmenu(
    BuildContext context,
    Offset position,
    List<dynamic> albums,
    Function(String) onTap,
  ) {
    _removeSubmenu();

    _submenuOverlay = OverlayEntry(
      builder: (_) => Positioned(
        left: position.dx + 8,
        top: position.dy,
        child: Material(
          elevation: 6,
          child: Container(
            width: 220,
            color: Colors.white,
            child: ListView(
              shrinkWrap: true,
              children: albums.map<Widget>((album) {
                final parsed = jsonDecode(album);
                return ListTile(
                  title: Text(parsed['album_name']),
                  onTap: () async {
                    await onTap(parsed['album_serial']);
                    _removeSubmenu();
                    Navigator.of(context).pop();
                  },
                );
              }).toList(),
            ),
          ),
        ),
      ),
    );

    Overlay.of(context).insert(_submenuOverlay!);
  }

  void _removeSubmenu() {
    _submenuOverlay?.remove();
    _submenuOverlay = null;
  }

  @override
  Widget build(BuildContext context) {
    if (error != null) {
      return Center(
        child: Text(error!, style: const TextStyle(color: Colors.red)),
      );
    }

    if (imageData == null) {
      return const Center(child: CircularProgressIndicator());
    }

    final tags = (imageData!['picture_tags'] as String? ?? '')
        .split(',')
        .where((e) => e.isNotEmpty)
        .toList();

    final people = (imageData!['picture_people'] as String? ?? '')
        .split(',')
        .where((e) => e.isNotEmpty)
        .toList();

    return Dialog(
      insetPadding: const EdgeInsets.all(24),
      child: Stack(
        children: [
          Padding(
            padding: const EdgeInsets.all(16),
            child: ConstrainedBox(
              constraints: BoxConstraints(
                maxHeight: MediaQuery.of(context).size.height * 0.8,
              ),
              child: SingleChildScrollView(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        PopupMenuButton<int>(
                          icon: const Icon(Icons.more_vert),
                          onSelected: (value) {
                            _removeSubmenu();
                            if (value == 0) _toggleFavourite();
                            if (value == 3) _editPicture();
                          },
                          onCanceled: _removeSubmenu,
                          itemBuilder: (context) => [
                            PopupMenuItem(
                              value: 0,
                              child: Text(
                                imageData!['is_favourite']
                                    ? 'Remove from Favourites'
                                    : 'Add to Favourites',
                              ),
                            ),
                            PopupMenuItem(
                              child: MouseRegion(
                                cursor: SystemMouseCursors.click,
                                onEnter: (event) => _showSubmenu(
                                  context,
                                  event.position,
                                  imageData!['not_in_custom_albums'] ?? [],
                                  _addToAlbum,
                                ),
                                child: const Row(
                                  mainAxisAlignment:
                                      MainAxisAlignment.spaceBetween,
                                  children: [
                                    Text(
                                      'Add to Custom Album',
                                      style: TextStyle(color: Colors.black),
                                    ),
                                    Icon(
                                      Icons.arrow_right,
                                      color: Colors.black,
                                    ),
                                  ],
                                ),
                              ),
                            ),
                            PopupMenuItem(
                              child: MouseRegion(
                                cursor: SystemMouseCursors.click,
                                onEnter: (event) => _showSubmenu(
                                  context,
                                  event.position,
                                  imageData!['in_custom_albums'] ?? [],
                                  _removeFromAlbum,
                                ),
                                child: const Row(
                                  mainAxisAlignment:
                                      MainAxisAlignment.spaceBetween,
                                  children: [
                                    Text(
                                      'Remove from Custom Album',
                                      style: TextStyle(color: Colors.black),
                                    ),
                                    Icon(
                                      Icons.arrow_right,
                                      color: Colors.black,
                                    ),
                                  ],
                                ),
                              ),
                            ),
                            const PopupMenuItem(
                              value: 3,
                              child: Text('Edit Picture'),
                            ),
                          ],
                        ),
                        IconButton(
                          icon: const Icon(Icons.close),
                          onPressed: widget.closePopup,
                        ),
                      ],
                    ),
                    Text(
                      imageData!['picture_title'] ?? '',
                      style: Theme.of(context).textTheme.headlineSmall,
                    ),
                    const SizedBox(height: 12),
                    ConstrainedBox(
                      constraints: const BoxConstraints(maxHeight: 400),
                      child: Image.memory(
                        base64Decode(imageData!['imageUrl']),
                        fit: BoxFit.contain,
                      ),
                    ),
                    const SizedBox(height: 12),
                    Wrap(
                      spacing: 8,
                      children: tags.map((t) => Chip(label: Text(t))).toList(),
                    ),
                    const SizedBox(height: 8),
                    Wrap(
                      spacing: 8,
                      children: people
                          .map((p) => Chip(label: Text(p)))
                          .toList(),
                    ),
                  ],
                ),
              ),
            ),
          ),
          if (widget.hasPrevious)
            Positioned(
              left: 0,
              top: MediaQuery.of(context).size.height * 0.4,
              child: IconButton(
                icon: const Icon(Icons.arrow_back, size: 32),
                onPressed: widget.onPrevious,
              ),
            ),
          if (widget.hasNext)
            Positioned(
              right: 0,
              top: MediaQuery.of(context).size.height * 0.4,
              child: IconButton(
                icon: const Icon(Icons.arrow_forward, size: 32),
                onPressed: widget.onNext,
              ),
            ),
        ],
      ),
    );
  }

  @override
  void dispose() {
    _removeSubmenu();
    super.dispose();
  }
}
