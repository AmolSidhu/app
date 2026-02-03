import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;
import 'package:flutter_frontend/static/constants.dart';
import 'package:flutter_frontend/pages/pictures/defaultPicturePage.dart';

class DefaultAlbumsRequest extends StatefulWidget {
  const DefaultAlbumsRequest({Key? key}) : super(key: key);

  @override
  State<DefaultAlbumsRequest> createState() => _DefaultAlbumsRequestState();
}

class _DefaultAlbumsRequestState extends State<DefaultAlbumsRequest> {
  final FlutterSecureStorage _secureStorage = FlutterSecureStorage();
  late Future<List<dynamic>> _albumsFuture;

  Future<List<dynamic>> _fetchAlbums() async {
    final token = await _secureStorage.read(key: 'token');
    if (token == null) {
      throw Exception('Authorization token not found.');
    }

    final response = await http.get(
      Uri.parse('$server/get/albums'),
      headers: <String, String>{'Authorization': token},
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body)['data'];
      return data;
    } else {
      throw Exception(jsonDecode(response.body)['message']);
    }
  }

  @override
  void initState() {
    super.initState();
    _albumsFuture = _fetchAlbums();
  }

  Future<void> _onAlbumTap(String albumSerial) async {
    await _secureStorage.write(key: 'defaultAlbumSerial', value: albumSerial);

    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => DefaultPicturePage(pictureId: albumSerial),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<List<dynamic>>(
      future: _albumsFuture,
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const Center(child: CircularProgressIndicator());
        } else if (snapshot.hasError) {
          return Center(child: Text('Error: ${snapshot.error}'));
        } else if (!snapshot.hasData || snapshot.data!.isEmpty) {
          return const Center(child: Text('No albums found.'));
        }

        final albums = snapshot.data!;
        return ListView.builder(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          itemCount: albums.length,
          itemBuilder: (context, index) {
            final album = albums[index];
            return ListTile(
              title: Text(album['album_name']),
              subtitle: Text(album['album_description']),
              onTap: () => _onAlbumTap(album['album_serial']),
            );
          },
        );
      },
    );
  }
}
