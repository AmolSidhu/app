import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter_frontend/static/constants.dart';
import 'videoListRequest.dart';

class VideoGenreRequest extends StatefulWidget {
  const VideoGenreRequest({Key? key}) : super(key: key);

  @override
  State<VideoGenreRequest> createState() => _VideoGenreRequestState();
}

class _VideoGenreRequestState extends State<VideoGenreRequest> {
  final _storage = const FlutterSecureStorage();
  List<String> _genres = [];
  bool _loading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _fetchGenres();
  }

  Future<void> _fetchGenres() async {
    try {
      final token = await _storage.read(key: 'token');
      final response = await http.get(
        Uri.parse('$server/get/genres/'),
        headers: {'Authorization': token ?? ''},
      );

      if (response.statusCode != 200)
        throw Exception('HTTP error: ${response.statusCode}');
      final data = jsonDecode(response.body);
      final genresList = (data['genres'] as List)
          .map((g) => g['genre'] as String)
          .toList();

      if (!mounted) return;
      setState(() {
        _genres = genresList;
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
    if (_loading) return const Center(child: CircularProgressIndicator());
    if (_error != null) return Center(child: Text('Error: $_error'));

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: _genres.map((genre) {
        return Padding(
          padding: const EdgeInsets.only(bottom: 32),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(genre, style: Theme.of(context).textTheme.titleLarge),
              const SizedBox(height: 8),
              VideoListRequest(videosEndpoint: '/get/videos_by_genre/$genre/'),
            ],
          ),
        );
      }).toList(),
    );
  }
}
