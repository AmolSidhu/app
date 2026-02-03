import 'package:flutter/material.dart';

import 'package:flutter_frontend/assets/articles/forms/articleFileUploadForm.dart';
import 'package:flutter_frontend/assets/articles/forms/articleUploadForm.dart';

class ArticleUploadSwitch extends StatefulWidget {
  const ArticleUploadSwitch({Key? key}) : super(key: key);

  @override
  State<ArticleUploadSwitch> createState() => _ArticleUploadSwitchState();
}

class _ArticleUploadSwitchState extends State<ArticleUploadSwitch> {
  bool isFileUpload = false;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            _ToggleButton(
              label: 'Standard Upload',
              active: !isFileUpload,
              onTap: () => setState(() => isFileUpload = false),
            ),
            const SizedBox(width: 8),
            _ToggleButton(
              label: 'File Upload',
              active: isFileUpload,
              onTap: () => setState(() => isFileUpload = true),
            ),
          ],
        ),

        const SizedBox(height: 20),

        Expanded(
          child: AnimatedSwitcher(
            duration: const Duration(milliseconds: 250),
            child: isFileUpload
                ? const ArticleFileUploadForm(key: ValueKey('file'))
                : const ArticleUploadForm(key: ValueKey('standard')),
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
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        decoration: BoxDecoration(
          color: active ? Theme.of(context).primaryColor : Colors.grey[300],
          borderRadius: BorderRadius.circular(8),
        ),
        child: Text(
          label,
          style: TextStyle(color: active ? Colors.white : Colors.black),
        ),
      ),
    );
  }
}
