import 'package:flutter/material.dart';

import 'package:flutter_frontend/assets/analytics/forms/editDataSourceForm.dart';
import 'package:flutter_frontend/assets/analytics/forms/uploadDataSourceForm.dart';

class DataSourceSwitch extends StatefulWidget {
  const DataSourceSwitch({Key? key}) : super(key: key);

  @override
  State<DataSourceSwitch> createState() => _DataSourceSwitchState();
}

class _DataSourceSwitchState extends State<DataSourceSwitch> {
  bool isUpload = false;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            _ToggleButton(
              label: 'Edit Data Source',
              active: !isUpload,
              onTap: () => setState(() => isUpload = false),
            ),
            const SizedBox(width: 8),
            _ToggleButton(
              label: 'Upload Data Source',
              active: isUpload,
              onTap: () => setState(() => isUpload = true),
            ),
          ],
        ),

        const SizedBox(height: 20),

        Expanded(
          child: AnimatedSwitcher(
            duration: const Duration(milliseconds: 250),
            child: isUpload
                ? const UploadDataSourceForm(key: ValueKey('upload'))
                : const EditDataSourceForm(key: ValueKey('edit')),
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
