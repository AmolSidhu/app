import 'dart:async';
import 'dart:convert';
import 'dart:html' as html;
import 'dart:ui_web' as ui_web;

import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;
import 'package:flutter_frontend/static/constants.dart';

class VideoStreamRequest extends StatefulWidget {
  final String serial;
  final bool resume;

  const VideoStreamRequest({
    Key? key,
    required this.serial,
    required this.resume,
  }) : super(key: key);

  @override
  State<VideoStreamRequest> createState() => _VideoStreamRequestState();
}

class _VideoStreamRequestState extends State<VideoStreamRequest> {
  final FlutterSecureStorage _storage = const FlutterSecureStorage();
  html.VideoElement? _videoElement;
  Timer? _timer;
  bool loading = true;
  String? error;

  static bool _videoViewRegistered = false;

  @override
  void initState() {
    super.initState();
    _initVideo();
  }

  @override
  void didUpdateWidget(covariant VideoStreamRequest oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.serial != widget.serial ||
        oldWidget.resume != widget.resume) {
      _disposeVideo();
      _initVideo();
    }
  }

  Future<void> _initVideo() async {
    setState(() {
      loading = true;
      error = null;
    });

    try {
      final token = await _storage.read(key: 'token');
      if (token == null) {
        setState(() {
          error = 'Missing authentication token';
          loading = false;
        });
        return;
      }

      final src =
          '$server/get/video_stream/${widget.serial}/$token/?resume=${widget.resume}';

      final resumeResponse = await http.get(
        Uri.parse(src),
        headers: {'Authorization': token},
      );

      if (resumeResponse.statusCode != 200) {
        throw Exception('Failed to fetch resume time');
      }

      final resumeTime =
          double.tryParse(resumeResponse.headers['resume-time'] ?? '0') ?? 0;

      _videoElement = html.VideoElement()
        ..src = src
        ..controls = true
        ..preload = 'auto'
        ..style.width = '640px'
        ..style.height = '360px'
        ..style.objectFit = 'contain';

      _videoElement!.onLoadedMetadata.listen((_) {
        if (widget.resume && resumeTime > 0) {
          _videoElement!.currentTime = resumeTime;
        }
      });

      if (!_videoViewRegistered) {
        ui_web.platformViewRegistry.registerViewFactory(
          'video-player',
          (int viewId) => _videoElement!,
        );
        _videoViewRegistered = true;
      }

      _timer = Timer.periodic(const Duration(seconds: 5), (_) {
        _updatePlaybackTime(widget.serial, token);
      });

      setState(() => loading = false);
    } catch (e) {
      debugPrint(e.toString());
      setState(() {
        error = 'Failed to load video';
        loading = false;
      });
    }
  }

  Future<void> _updatePlaybackTime(String serial, String token) async {
    if (_videoElement == null) return;
    try {
      await http.post(
        Uri.parse('$server/update/playback_time/$serial/'),
        headers: {'Authorization': token, 'Content-Type': 'application/json'},
        body: jsonEncode({
          'serial': serial,
          'currentTime': _videoElement!.currentTime,
        }),
      );
    } catch (e) {
      debugPrint('Playback update failed: $e');
    }
  }

  void _disposeVideo() {
    _timer?.cancel();
    _videoElement?.pause();
    _videoElement = null;
  }

  @override
  void dispose() {
    _disposeVideo();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return loading
        ? const SizedBox(
            width: 640,
            height: 360,
            child: Center(child: CircularProgressIndicator()),
          )
        : error != null
        ? SizedBox(width: 640, height: 360, child: Center(child: Text(error!)))
        : SizedBox(
            width: 640,
            height: 360,
            child: const HtmlElementView(viewType: 'video-player'),
          );
  }
}
