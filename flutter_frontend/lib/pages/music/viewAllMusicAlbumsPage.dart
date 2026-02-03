import 'package:flutter/material.dart';
import 'package:flutter_frontend/assets/music/requests/musicAlbumRequest.dart';

class ViewAllMusicAlbumsPage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('All Music Albums')),
      body: Center(child: MusicAlbumRequest()),
    );
  }
}
