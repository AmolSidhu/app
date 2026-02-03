import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:flutter_frontend/pages/videos/videoTitleSearchPage.dart';

class VideoTitleSearchRequest extends StatefulWidget {
  const VideoTitleSearchRequest({Key? key}) : super(key: key);

  @override
  State<VideoTitleSearchRequest> createState() =>
      _VideoTitleSearchRequestState();
}

class _VideoTitleSearchRequestState extends State<VideoTitleSearchRequest> {
  final storage = const FlutterSecureStorage();
  final TextEditingController _controller = TextEditingController();

  String? error;
  bool isSubmitting = false;

  Future<void> _handleSearch() async {
    final query = _controller.text.trim();

    if (query.isEmpty) return;

    setState(() {
      isSubmitting = true;
      error = null;
    });

    try {
      await storage.write(key: 'videoTitleSearchQuery', value: query);

      if (!mounted) return;

      await Navigator.push(
        context,
        MaterialPageRoute(builder: (_) => VideoTitleSearchPage()),
      );
    } catch (e) {
      if (mounted) {
        setState(() {
          error = 'Failed to store search query';
        });
      }
    } finally {
      if (mounted) {
        _controller.clear();
        setState(() {
          isSubmitting = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Center(
      child: SizedBox(
        width: 400,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              controller: _controller,
              onSubmitted: (_) => _handleSearch(),
              decoration: const InputDecoration(
                hintText: 'Search...',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 12),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: isSubmitting ? null : _handleSearch,
                child: isSubmitting
                    ? const SizedBox(
                        height: 20,
                        width: 20,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    : const Text('Search'),
              ),
            ),
            if (error != null) ...[
              const SizedBox(height: 8),
              Text(error!, style: const TextStyle(color: Colors.red)),
            ],
          ],
        ),
      ),
    );
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }
}
