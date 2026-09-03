import 'package:flutter/material.dart';
import 'package:flutter_frontend/assets/youtube/requests/youtubePlaylistsRequest.dart';
import 'package:flutter_frontend/assets/youtube/popups/createYoutubePlaylistPopup.dart';

class MyYoutubeListsPage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('My YouTube Lists')),
      body: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'My YouTube Playlists',
                  style: Theme.of(context).textTheme.headlineSmall,
                ),
                ElevatedButton.icon(
                  icon: const Icon(Icons.add),
                  label: const Text('Add Playlist'),
                  onPressed: () {
                    showDialog(
                      context: context,
                      useRootNavigator: true,
                      builder: (context) => CreateYoutubePlaylistPopup(
                        onClose: () =>
                            Navigator.of(context, rootNavigator: true).pop(),
                      ),
                    );
                  },
                ),
              ],
            ),

            const SizedBox(height: 24),

            Expanded(child: YoutubePlaylistsRequest()),
          ],
        ),
      ),
    );
  }
}
