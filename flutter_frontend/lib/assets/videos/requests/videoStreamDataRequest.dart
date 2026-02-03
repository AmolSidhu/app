import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;
import 'package:flutter_frontend/static/constants.dart';

class VideoStreamDataRequest extends StatefulWidget {
  final Function(String serial) onSerialChange;

  const VideoStreamDataRequest({Key? key, required this.onSerialChange})
    : super(key: key);

  @override
  State<VideoStreamDataRequest> createState() => _VideoStreamDataRequestState();
}

class _VideoStreamDataRequestState extends State<VideoStreamDataRequest> {
  final FlutterSecureStorage _storage = const FlutterSecureStorage();

  bool loading = true;
  String? error;
  List<dynamic> streams = [];

  @override
  void initState() {
    super.initState();
    _fetchStreamData();
  }

  Future<void> _fetchStreamData() async {
    setState(() => loading = true);
    try {
      final token = await _storage.read(key: 'token');
      final serial = await _storage.read(key: 'videoSerial');

      if (token == null || serial == null) {
        setState(() {
          error = 'Missing authentication or video information';
          loading = false;
        });
        return;
      }

      final response = await http.get(
        Uri.parse('$server/get/next_previous_episode/$serial/'),
        headers: {'Authorization': token, 'Content-Type': 'application/json'},
      );

      if (response.statusCode != 200) {
        throw Exception('Failed to fetch data: ${response.statusCode}');
      }

      final decoded = json.decode(response.body);
      setState(() {
        streams = decoded['data'];
        loading = false;
        error = null;
      });
    } catch (e) {
      setState(() {
        error = e.toString();
        loading = false;
      });
    }
  }

  Future<void> _handleNavigation(String serial) async {
    await _storage.write(key: 'videoSerial', value: serial);
    await _storage.write(key: 'videoResume', value: 'false');

    widget.onSerialChange(serial);
    _fetchStreamData();
  }

  @override
  Widget build(BuildContext context) {
    if (loading) return const Center(child: CircularProgressIndicator());
    if (error != null) return Center(child: Text('Error: $error'));
    if (streams.isEmpty) return const Center(child: Text('No data available'));

    return ListView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      padding: const EdgeInsets.all(16),
      itemCount: streams.length,
      itemBuilder: (context, index) {
        final stream = streams[index];
        return Card(
          margin: const EdgeInsets.symmetric(vertical: 8),
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    if (stream['previous_video_serial'] != null)
                      ElevatedButton(
                        onPressed: () =>
                            _handleNavigation(stream['previous_video_serial']),
                        child: Text(
                          '← Previous Episode Season ${stream['previous_season']} Episode ${stream['previous_episode']}',
                        ),
                      ),
                    if (stream['next_video_serial'] != null)
                      ElevatedButton(
                        onPressed: () =>
                            _handleNavigation(stream['next_video_serial']),
                        child: Text(
                          'Next Episode Season ${stream['next_season']} Episode ${stream['next_episode']} →',
                        ),
                      ),
                  ],
                ),
                const SizedBox(height: 12),
                Text(
                  stream['title'] ?? 'Untitled',
                  style: Theme.of(
                    context,
                  ).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 8),
                Text(
                  stream['description'] ?? '',
                  style: Theme.of(context).textTheme.bodyMedium,
                ),
              ],
            ),
          ),
        );
      },
    );
  }
}
