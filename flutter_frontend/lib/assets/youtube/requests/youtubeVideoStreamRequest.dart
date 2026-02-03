import 'dart:async';
import 'dart:convert';
import 'dart:html' as html;
import 'dart:ui_web' as ui_web;

import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;
import 'package:flutter_frontend/static/constants.dart';

class YoutubeVideoStreamRequest extends StatefulWidget {
  final String videoSerial;

  const YoutubeVideoStreamRequest({Key? key, required this.videoSerial})
    : super(key: key);

  @override
  State<YoutubeVideoStreamRequest> createState() =>
      _YoutubeVideoStreamRequestState();
}

class _YoutubeVideoStreamRequestState extends State<YoutubeVideoStreamRequest> {
  final FlutterSecureStorage _storage = const FlutterSecureStorage();

  static html.VideoElement? _videoElement;
  static bool _registered = false;

  Timer? _timer;
  bool _loading = true;
  String? _error;

  @override
  void initState() {
    super.initState();

    _videoElement ??= html.VideoElement()
      ..controls = true
      ..autoplay = false
      ..preload = 'auto'
      ..style.width = '100%'
      ..style.height = '100%'
      ..style.objectFit = 'contain';

    if (!_registered) {
      ui_web.platformViewRegistry.registerViewFactory(
        'youtube-video-player',
        (int viewId) => _videoElement!,
      );
      _registered = true;
    }

    _loadVideo();
  }

  @override
  void didUpdateWidget(covariant YoutubeVideoStreamRequest oldWidget) {
    super.didUpdateWidget(oldWidget);

    if (oldWidget.videoSerial != widget.videoSerial) {
      _loadVideo();
    }
  }

  Future<void> _loadVideo() async {
    setState(() {
      _loading = true;
      _error = null;
    });

    _timer?.cancel();

    try {
      final token = await _storage.read(key: 'token');
      if (token == null) throw Exception('Missing token');

      final src =
          '$server/get/youtube_video_stream/${widget.videoSerial}/$token/';

      final resumeResponse = await http.get(
        Uri.parse(src),
        headers: {'Authorization': token},
      );

      if (resumeResponse.statusCode != 200) {
        throw Exception('Failed to fetch resume time');
      }

      final resumeTime =
          double.tryParse(resumeResponse.headers['resume-time'] ?? '0') ?? 0;

      _videoElement!
        ..pause()
        ..src = src
        ..load();

      _videoElement!.onLoadedMetadata.first.then((_) {
        if (resumeTime > 0) {
          _videoElement!.currentTime = resumeTime;
        }
        _videoElement!.play();
      });

      _timer = Timer.periodic(const Duration(seconds: 5), (_) {
        _updatePlaybackTime(widget.videoSerial, token);
      });

      setState(() => _loading = false);
    } catch (e) {
      debugPrint(e.toString());
      setState(() {
        _error = 'Failed to load video';
        _loading = false;
      });
    }
  }

  Future<void> _updatePlaybackTime(String serial, String token) async {
    try {
      await http.post(
        Uri.parse('$server/update/youtube_playback_time/$serial/'),
        headers: {'Authorization': token, 'Content-Type': 'application/json'},
        body: jsonEncode({
          'serial': serial,
          'currentTime': _videoElement!.currentTime,
        }),
      );
    } catch (_) {}
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return const SizedBox(
        width: 640,
        height: 360,
        child: Center(child: CircularProgressIndicator()),
      );
    }

    if (_error != null) {
      return SizedBox(
        width: 640,
        height: 360,
        child: Center(child: Text(_error!)),
      );
    }

    return const SizedBox(
      width: 640,
      height: 360,
      child: HtmlElementView(viewType: 'youtube-video-player'),
    );
  }
}
