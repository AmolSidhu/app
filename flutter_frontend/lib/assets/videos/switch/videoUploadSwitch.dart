import 'package:flutter/material.dart';

import 'package:flutter_frontend/assets/videos/forms/singleVideoUploadForm.dart';
import 'package:flutter_frontend/assets/videos/forms/batchVideoUploadForm.dart';

class VideoUploadSwitch extends StatefulWidget {
  const VideoUploadSwitch({Key? key}) : super(key: key);

  @override
  State<VideoUploadSwitch> createState() => _VideoUploadSwitchState();
}

class _VideoUploadSwitchState extends State<VideoUploadSwitch> {
  bool isBatch = false;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            _ToggleButton(
              label: 'Single Upload',
              active: !isBatch,
              onTap: () => setState(() => isBatch = false),
            ),
            const SizedBox(width: 8),
            _ToggleButton(
              label: 'Batch Upload',
              active: isBatch,
              onTap: () => setState(() => isBatch = true),
            ),
          ],
        ),

        const SizedBox(height: 20),

        Expanded(
          child: AnimatedSwitcher(
            duration: const Duration(milliseconds: 250),
            child: isBatch
                ? const BatchVideoUploadForm(key: ValueKey('batch'))
                : const SingleVideoUploadForm(key: ValueKey('single')),
          ),
        ),
      ],
    );
  }
}

class _ToggleButton extends StatelessWidget {
  final String label;
  final bool active;
  final VoidCallback onTap;

  const _ToggleButton({
    required this.label,
    required this.active,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return ElevatedButton(
      style: ElevatedButton.styleFrom(
        backgroundColor: active ? Colors.blue : Colors.grey[300],
        foregroundColor: active ? Colors.white : Colors.black,
      ),
      onPressed: onTap,
      child: Text(label),
    );
  }
}
