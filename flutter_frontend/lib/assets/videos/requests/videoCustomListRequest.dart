import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter_frontend/static/constants.dart';
import 'videoListRequest.dart';

class VideoCustomListRequest extends StatefulWidget {
  const VideoCustomListRequest({Key? key}) : super(key: key);

  @override
  State<VideoCustomListRequest> createState() => _VideoCustomListRequestState();
}

class _VideoCustomListRequestState extends State<VideoCustomListRequest> {
  final _storage = const FlutterSecureStorage();

  List<Map<String, String>> _customLists = [];

  bool _loading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _fetchCustomLists();
  }

  Future<void> _fetchCustomLists() async {
    try {
      final token = await _storage.read(key: 'token');

      final response = await http.get(
        Uri.parse('$server/get/custom_video_lists/'),
        headers: {'Authorization': token ?? ''},
      );

      if (response.statusCode != 200) {
        throw Exception('HTTP error: ${response.statusCode}');
      }

      final decoded = jsonDecode(response.body);

      final List<Map<String, String>> lists = (decoded['data'] as List)
          .map<Map<String, String>>((item) {
            return {
              'name': item['list_name'].toString(),
              'serial': item['list_serial'].toString(),
            };
          })
          .toList();

      if (!mounted) return;

      setState(() {
        _customLists = lists;
        _loading = false;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _error = e.toString();
        _loading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return const Center(child: CircularProgressIndicator());
    }

    if (_error != null) {
      return Center(child: Text('Error: $_error'));
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: _customLists.map((list) {
        return Padding(
          padding: const EdgeInsets.only(bottom: 32),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                list['name']!,
                style: Theme.of(context).textTheme.titleLarge,
              ),
              const SizedBox(height: 8),
              VideoListRequest(
                videosEndpoint: '/get/custom_list_videos/${list['serial']}/',
              ),
            ],
          ),
        );
      }).toList(),
    );
  }
}
