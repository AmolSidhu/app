import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter_frontend/static/constants.dart';

class ServerMetaDataPopup extends StatefulWidget {
  final VoidCallback onClose;

  const ServerMetaDataPopup({required this.onClose, Key? key})
    : super(key: key);

  @override
  State<ServerMetaDataPopup> createState() => _ServerMetaDataPopupState();
}

class _ServerMetaDataPopupState extends State<ServerMetaDataPopup> {
  final _storage = const FlutterSecureStorage();

  Map<String, dynamic>? _metadata;
  String? _error;
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _fetchServerData();
  }

  Future<void> _fetchServerData() async {
    try {
      final token = await _storage.read(key: 'token');
      if (token == null) throw Exception('Token not found');

      final response = await http.get(
        Uri.parse('$server/get/server/metadata/'),
        headers: {'Authorization': token},
      );

      final body = jsonDecode(response.body);

      if (response.statusCode == 200) {
        setState(() {
          _metadata = body['data'];
          _isLoading = false;
        });
      } else {
        setState(() {
          _error = body['message'] ?? 'Failed to fetch server metadata.';
          _isLoading = false;
        });
      }
    } catch (_) {
      setState(() {
        _error = 'Internal error. Please try again later.';
        _isLoading = false;
      });
    }
  }

  Widget _infoRow(String label, String? value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 10),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 220,
            child: Text(
              label,
              style: const TextStyle(fontWeight: FontWeight.bold),
            ),
          ),
          Expanded(child: Text(value ?? '—')),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Center(
      child: ConstrainedBox(
        constraints: BoxConstraints(
          maxWidth: MediaQuery.of(context).size.width * 0.85,
          maxHeight: MediaQuery.of(context).size.height * 0.85,
        ),
        child: Material(
          elevation: 12,
          borderRadius: BorderRadius.circular(16),
          color: Colors.white,
          child: Column(
            children: [
              Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: 24,
                  vertical: 18,
                ),
                decoration: BoxDecoration(
                  color: Colors.blueGrey.shade50,
                  borderRadius: const BorderRadius.vertical(
                    top: Radius.circular(16),
                  ),
                ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Text(
                      'Application Information',
                      style: TextStyle(
                        fontSize: 22,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    IconButton(
                      icon: const Icon(Icons.close),
                      onPressed: widget.onClose,
                    ),
                  ],
                ),
              ),

              Expanded(
                child: _isLoading
                    ? const Center(child: CircularProgressIndicator())
                    : _error != null
                    ? Center(
                        child: Text(
                          _error!,
                          style: const TextStyle(color: Colors.red),
                        ),
                      )
                    : SingleChildScrollView(
                        padding: const EdgeInsets.all(32),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            _infoRow('Version', _metadata?['version']),
                            _infoRow('Environment', _metadata?['enviroment']),
                            _infoRow('Database', _metadata?['database']),
                            _infoRow(
                              'Selenium Driver',
                              _metadata?['selenium_driver_version'],
                            ),
                            _infoRow(
                              'Last Updated',
                              _metadata?['last_updated'],
                            ),
                            _infoRow(
                              'Other Requirements',
                              (_metadata?['other_requirements'] as List?)?.join(
                                ', ',
                              ),
                            ),
                          ],
                        ),
                      ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
