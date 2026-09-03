import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

import 'package:flutter_frontend/assets/videos/requests/videoStreamRequest.dart';
import 'package:flutter_frontend/assets/videos/requests/videoStreamDataRequest.dart';
import 'package:flutter_frontend/assets/videos/requests/videoSuggestionsRequest.dart';

class VideoStreamPage extends StatefulWidget {
  const VideoStreamPage({Key? key}) : super(key: key);

  @override
  State<VideoStreamPage> createState() => _VideoStreamPageState();
}

class _VideoStreamPageState extends State<VideoStreamPage> {
  final FlutterSecureStorage _storage = const FlutterSecureStorage();

  String? currentSerial;
  bool resume = true;

  @override
  void initState() {
    super.initState();
    _loadInitialSerial();
  }

  Future<void> _loadInitialSerial() async {
    final serial = await _storage.read(key: 'videoSerial');
    final resumeValue = await _storage.read(key: 'videoResume');

    setState(() {
      currentSerial = serial;
      resume = resumeValue != 'false';
    });
  }

  void _handleSerialChange(String serial) {
    setState(() {
      currentSerial = serial;
      resume = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    if (currentSerial == null) {
      return const Center(child: CircularProgressIndicator());
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.all(16.0),
          child: Row(
            children: [
              IconButton(
                icon: const Icon(Icons.arrow_back),
                onPressed: () => Navigator.of(context).pop(),
              ),
              const SizedBox(width: 8),
              const Text(
                'Video Stream Page',
                style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
              ),
            ],
          ),
        ),

        Expanded(
          child: SingleChildScrollView(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Padding(
                  padding: const EdgeInsets.all(16),
                  child: VideoStreamRequest(
                    serial: currentSerial!,
                    resume: resume,
                  ),
                ),

                VideoStreamDataRequest(onSerialChange: _handleSerialChange),

                const Padding(
                  padding: EdgeInsets.only(top: 8),
                  child: VideoSuggestionsRequest(),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }
}
