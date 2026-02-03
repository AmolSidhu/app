import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;
import 'package:flutter_frontend/static/constants.dart';
import 'package:flutter_frontend/pages/management/editYoutubeVideoPage.dart';

class YoutubeStreamInfoRequest extends StatefulWidget {
  const YoutubeStreamInfoRequest({Key? key}) : super(key: key);

  @override
  State<YoutubeStreamInfoRequest> createState() =>
      _YoutubeStreamInfoRequestState();
}

class _YoutubeStreamInfoRequestState extends State<YoutubeStreamInfoRequest> {
  final FlutterSecureStorage _storage = const FlutterSecureStorage();

  bool _loading = true;
  String? _error;
  Map<String, dynamic>? _streamInfo;

  @override
  void initState() {
    super.initState();
    _fetchStreamInfo();
  }

  Future<void> _fetchStreamInfo() async {
    setState(() {
      _loading = true;
      _error = null;
    });

    try {
      final token = await _storage.read(key: 'token');
      final youtubeSerial = await _storage.read(key: 'youtubeSerial');

      if (token == null || youtubeSerial == null) {
        setState(() {
          _error = 'Missing authentication token or YouTube serial.';
          _loading = false;
        });
        return;
      }

      final response = await http.get(
        Uri.parse('$server/get/youtube_stream_data/$youtubeSerial/'),
        headers: {'Authorization': token, 'Content-Type': 'application/json'},
      );

      if (response.statusCode != 200) {
        final errorData = json.decode(response.body);
        throw Exception(errorData['message'] ?? 'Failed to fetch stream info.');
      }

      final jsonData = json.decode(response.body);

      setState(() {
        _streamInfo = jsonData['data'];
        _loading = false;
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
        _loading = false;
      });
    }
  }

  Future<void> _onEditPressed() async {
    await _storage.write(
      key: 'editYoutubeVideoSerial',
      value: _streamInfo!['serial'].toString(),
    );

    if (!mounted) return;
    Navigator.of(
      context,
    ).push(MaterialPageRoute(builder: (_) => EditYoutubeVideoPage()));
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    }

    if (_error != null) {
      return Scaffold(
        body: Center(
          child: Text(
            _error!,
            style: const TextStyle(color: Colors.red),
            textAlign: TextAlign.center,
          ),
        ),
      );
    }

    return Scaffold(
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24.0),
        child: Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 800),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.center,
              children: [
                Text(
                  _streamInfo!['title'],
                  style: Theme.of(context).textTheme.headlineMedium,
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 16),
                Text(_streamInfo!['description'], textAlign: TextAlign.center),
                const SizedBox(height: 32),

                ElevatedButton.icon(
                  onPressed: _onEditPressed,
                  icon: const Icon(Icons.edit),
                  label: const Text('Edit Video'),
                  style: ElevatedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 32,
                      vertical: 16,
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
