import os
import re
from pathlib import Path


class RenameEngine:
    def __init__(self):
        # 预览数据存储
        self.preview_data = []
        # 重命名历史记录（用于撤销）
        self.undo_history = []
        # 撤销操作对应的目录
        self.undo_dir = ""
        # 临时文件名前缀（防止重命名冲突）
        self.temp_prefix = "__temp_rename__"

    # ============ 私有辅助方法 ============

    @staticmethod
    def _natural_sort_key(name: str):
        """
        自然排序 key：把文件名拆分成 数字段/非数字段，
        数字段转成 int 比较，这样 "2" 会排在 "10" 前面，
        而不是按字符逐位比较的字典序（那样会得到 1, 10, 100, 2, ...）。
        """
        return [int(part) if part.isdigit() else part.lower()
                for part in re.split(r'(\d+)', name)]

    def _get_filtered_files(self, directory_path: str, extensions: list = None) -> list:
        """
        统一的目录校验与文件过滤逻辑
        返回 Path 对象列表
        """
        if not directory_path or not os.path.exists(directory_path):
            raise ValueError("msg_select_dir")

        dir_path = Path(directory_path)
        valid_files = []

        # 统一处理扩展名，全部转为小写并确保带 '.'
        if extensions:
            extensions = [ext.lower() if ext.startswith('.') else f".{ext.lower()}" for ext in extensions]

        for file_path in dir_path.iterdir():
            # 跳过文件夹
            if file_path.is_dir():
                continue

            # 跳过可能遗留的临时文件（防止二次污染）
            if file_path.name.startswith(self.temp_prefix):
                continue

            # 扩展名过滤
            if extensions and file_path.suffix.lower() not in extensions:
                continue

            valid_files.append(file_path)

        return valid_files

    def _extract_number_group(self, filename: str, group_index: int):
        """
        提取文件名中第 group_index 组数字（从1开始）
        返回 int 或 None
        """
        pattern = re.compile(r'(\d+)')
        matches = pattern.findall(filename)

        if not matches or group_index < 1 or group_index > len(matches):
            return None

        try:
            return int(matches[group_index - 1])
        except ValueError:
            return None

    def _replace_number_group(self, text: str, group_index: int, replace_with: str) -> str:
        """
        替换文本中第 group_index 组数字（从1开始）
        返回替换后的字符串
        """
        pattern = re.compile(r'(\d+)')
        # 使用列表作为可变容器，避免 nonlocal 在嵌套函数中的问题
        counter = [group_index]

        def replace_func(match):
            counter[0] -= 1
            if counter[0] == 0:
                return replace_with
            return match.group(0)

        return pattern.sub(replace_func, text)

    # ============ 文件获取方法 ============

    def get_files_by_range(self, directory_path: str, extensions: list = None) -> list:
        """
        获取文件并按名称自然排序（供 Tab 1 使用）
        返回 Path 对象列表
        """
        files = self._get_filtered_files(directory_path, extensions)
        return sorted(files, key=lambda x: self._natural_sort_key(x.name))

    def get_files_by_order(self, directory_path: str, extensions: list = None) -> list:
        """
        获取文件（按名称排序）
        返回 Path 对象列表
        """
        return self.get_files_by_range(directory_path, extensions)

    def get_files_by_time(self, directory_path: str, extensions: list = None, reverse: bool = False) -> list:
        """
        获取文件并按修改时间排序（供 Tab 2 使用）
        返回 Path 对象列表
        """
        files = self._get_filtered_files(directory_path, extensions)
        return sorted(files, key=lambda x: x.stat().st_mtime, reverse=reverse)

    def get_all_files(self, directory_path: str) -> list:
        """
        获取目录下所有有效文件（不进行扩展名过滤）
        返回 Path 对象列表
        """
        return self._get_filtered_files(directory_path, None)

    # ============ 预览数据生成方法 ============

    def generate_preview_from_list(self, file_list: list, prefix: str, start_num: int,
                                   padding: int, new_extension: str = None, 
                                   reverse: bool = False, is_prefix: bool = True) -> list:
        """
        根据传入的文件列表生成重命名预览数据
        :param file_list: Path 对象列表或文件路径字符串列表
        :param prefix: 新文件名前缀
        :param start_num: 起始序号
        :param padding: 序号补零位数
        :param new_extension: 新后缀名 (如果为空则保持原后缀)
        :param reverse: 是否倒序编号
        :param is_prefix: True=前缀模式，False=后缀模式
        :return: 预览数据列表 (old_name, temp_name, new_name)
        """
        self.preview_data = []
        assigned_names = set()

        file_list = list(file_list)
        if reverse:
            file_list = file_list[::-1]

        for index, item in enumerate(file_list):
            file_path = Path(item)

            # 计算序号
            current_num = start_num + index
            num_str = str(current_num).zfill(padding) if padding > 0 else str(current_num)

            # 处理扩展名
            if new_extension is not None and new_extension.strip() != "":
                ext = new_extension if new_extension.startswith('.') else f".{new_extension}"
            else:
                ext = file_path.suffix

            # 组合新名称
            if is_prefix:
                base_new_name = f"{prefix}{num_str}"
            else:
                # 后缀模式：保留原文件名（不含扩展名）+ 后缀 + 编号
                base_new_name = f"{file_path.stem}{prefix}{num_str}"

            candidate_name = f"{base_new_name}{ext}"

            # 处理重名冲突
            counter = 1
            while candidate_name in assigned_names:
                candidate_name = f"{base_new_name}_{counter}{ext}"
                counter += 1

            assigned_names.add(candidate_name)
            temp_name = f"{self.temp_prefix}{candidate_name}"

            self.preview_data.append({
                'old_name': file_path.name,
                'new_name': candidate_name,
                'old_path': str(file_path),
                'new_path': str(file_path.with_name(candidate_name)),
                'temp_path': str(file_path.with_name(temp_name))
            })

        return self.preview_data

    def generate_preview_num(self, directory_path: str, prefix: str, start_num: int,
                             padding: int, extensions: list = None, 
                             reverse: bool = False, is_prefix: bool = True) -> list:
        """
        直接从目录生成序号预览（封装了 get_files_by_range 和 generate_preview_from_list）
        """
        files = self.get_files_by_range(directory_path, extensions)
        return self.generate_preview_from_list(files, prefix, start_num, padding, 
                                               new_extension=None, reverse=reverse, 
                                               is_prefix=is_prefix)

    def generate_preview_num_advanced(self, files, new_start: int, prefix: str,
                                      only_num: bool, num_group: int = 1,
                                      reverse: bool = False, pad_width: int = 0,
                                      is_prefix: bool = True,
                                      old_start: int = None, old_end: int = None) -> list:
        """
        高级序号预览生成（支持数字组提取、仅保留序号、前缀/后缀位置）
        :param files: 文件列表（Path 对象）
        :param new_start: 目标起始编号
        :param prefix: 前缀/后缀文本
        :param only_num: 是否仅保留序号
        :param num_group: 数字组序号（从1开始）
        :param reverse: 是否倒序
        :param pad_width: 补零位数
        :param is_prefix: True=前缀，False=后缀
        :param old_start: 当前编号范围起始值（为 None 时不做范围过滤）
        :param old_end: 当前编号范围结束值（为 None 时不做范围过滤）
        """
        self.preview_data = []
        assigned_names = set()

        if not files:
            return self.preview_data

        # 按文件名排序，提取数字
        file_list = []
        for f in files:
            num = self._extract_number_group(f.stem, num_group)
            if num is not None:
                file_list.append((num, f))
            else:
                file_list.append((float('inf'), f))

        # 当前编号范围过滤：只保留提取到的数字落在 [old_start, old_end] 内的文件
        # （没有提取到数字的文件在启用范围过滤时会被排除，因为无法判断其是否在范围内）
        if old_start is not None and old_end is not None:
            file_list = [(num, f) for num, f in file_list
                         if num != float('inf') and old_start <= num <= old_end]

        sorted_files = sorted(file_list, key=lambda x: x[0])

        # 如果倒序
        if reverse:
            sorted_files = sorted_files[::-1]

        for idx, (_, file_path) in enumerate(sorted_files):
            ext_part = file_path.suffix

            # 计算新编号
            raw_num = new_start + idx
            num_str = str(raw_num).zfill(pad_width) if pad_width > 0 else str(raw_num)

            if only_num:
                # 仅保留序号，去掉原文件名所有文本
                base_new_name = num_str
            else:
                # 前缀/后缀模式：原文件名一律丢弃，只保留 文本+编号 的组合
                # （效果类似 IMG_0001.jpg）
                if is_prefix:
                    # 前缀模式：前缀文本 + 编号
                    base_new_name = f"{prefix}{num_str}"
                else:
                    # 后缀模式：编号 + 后缀文本
                    base_new_name = f"{num_str}{prefix}"

            candidate_name = f"{base_new_name}{ext_part}"

            # 处理重名冲突
            counter = 1
            while candidate_name in assigned_names:
                candidate_name = f"{base_new_name}_{counter}{ext_part}"
                counter += 1

            assigned_names.add(candidate_name)
            temp_name = f"{self.temp_prefix}{candidate_name}"

            self.preview_data.append({
                'old_name': file_path.name,
                'new_name': candidate_name,
                'old_path': str(file_path),
                'new_path': str(file_path.with_name(candidate_name)),
                'temp_path': str(file_path.with_name(temp_name))
            })

        return self.preview_data

    def generate_preview_order(self, files, prefix: str, only_num: bool,
                               pad_width: int = 0, reverse: bool = False,
                               new_start: int = 1, is_prefix: bool = True,
                               sort_by_name: bool = True) -> list:
        """
        按顺序重命名预览生成
        :param files: Path 对象列表
        :param prefix: 前缀/后缀文本
        :param only_num: 是否仅保留序号
        :param pad_width: 补零位数
        :param reverse: 是否倒序
        :param new_start: 起始编号
        :param is_prefix: True=前缀，False=后缀
        :param sort_by_name: 是否在内部按文件名字母顺序重新排序。
            "按顺序重命名"Tab 需要 True（按名字排序）；
            "按时间重命名"Tab 传入的文件已经按修改时间排好，
            必须传 False，否则会被这里重新按文件名排序，
            导致"按时间重命名"名不副实（这是之前的 bug）。
        """
        self.preview_data = []
        assigned_names = set()

        file_list = list(files)

        if sort_by_name:
            # 自然排序——仅适用于按名字排序的场景
            file_list.sort(key=lambda x: self._natural_sort_key(x.name))

        if reverse:
            file_list = file_list[::-1]

        for idx, file_path in enumerate(file_list):
            ext_part = file_path.suffix

            # 计算编号
            raw_num = new_start + idx
            num_str = str(raw_num).zfill(pad_width) if pad_width > 0 else str(raw_num)

            if only_num:
                base_new_name = num_str
            else:
                # 前缀/后缀模式：原文件名一律丢弃，只保留 文本+编号 的组合
                # （效果类似 IMG_0001.jpg）
                if is_prefix:
                    # 前缀模式：前缀文本 + 编号
                    base_new_name = f"{prefix}{num_str}"
                else:
                    # 后缀模式：编号 + 后缀文本
                    base_new_name = f"{num_str}{prefix}"

            candidate_name = f"{base_new_name}{ext_part}"

            # 处理重名冲突
            counter = 1
            while candidate_name in assigned_names:
                candidate_name = f"{base_new_name}_{counter}{ext_part}"
                counter += 1

            assigned_names.add(candidate_name)
            temp_name = f"{self.temp_prefix}{candidate_name}"

            self.preview_data.append({
                'old_name': file_path.name,
                'new_name': candidate_name,
                'old_path': str(file_path),
                'new_path': str(file_path.with_name(candidate_name)),
                'temp_path': str(file_path.with_name(temp_name))
            })

        return self.preview_data

    def generate_preview_replace(self, files, find_text: str, replace_text: str,
                                  is_regex: bool) -> list:
        """
        查找与替换预览生成
        :param files: 文件名列表或 Path 对象列表
        :param find_text: 查找文本
        :param replace_text: 替换文本
        :param is_regex: 是否使用正则表达式
        """
        self.preview_data = []
        assigned_names = set()

        for item in files:
            if isinstance(item, Path):
                file_path = item
            else:
                file_path = Path(item)

            name_part = file_path.stem
            ext_part = file_path.suffix

            try:
                if is_regex:
                    base_new_name = re.sub(find_text, replace_text, name_part)
                else:
                    base_new_name = name_part.replace(find_text, replace_text)
            except re.error:
                raise re.error("msg_regex_err")

            # 如果名称没有变化，跳过
            if f"{base_new_name}{ext_part}" == file_path.name:
                continue

            candidate_name = f"{base_new_name}{ext_part}"

            # 处理重名冲突
            counter = 1
            while candidate_name in assigned_names:
                candidate_name = f"{base_new_name}_{counter}{ext_part}"
                counter += 1

            assigned_names.add(candidate_name)
            temp_name = f"{self.temp_prefix}{candidate_name}"

            self.preview_data.append({
                'old_name': file_path.name,
                'new_name': candidate_name,
                'old_path': str(file_path),
                'new_path': str(file_path.with_name(candidate_name)),
                'temp_path': str(file_path.with_name(temp_name))
            })

        return self.preview_data

    # ============ 执行方法 ============

    def execute_rename(self, preview_list: list = None, progress_callback=None) -> bool:
        """
        执行批量重命名（采用安全的2步重命名法）
        :param preview_list: 预览数据列表，如果为 None 则使用 self.preview_data
        :param progress_callback: 进度回调函数 callback(current, total)
        """
        if preview_list is None:
            preview_list = self.preview_data

        if not preview_list:
            raise ValueError("msg_preview_first")

        temp_renamed_items = []
        final_history = []
        total_steps = len(preview_list) * 2
        current_step = 0

        try:
            # 第一阶段：原名 -> 临时名
            for item in preview_list:
                old_p = Path(item['old_path'])
                temp_p = Path(item['temp_path'])

                if old_p.exists():
                    old_p.rename(temp_p)
                    temp_renamed_items.append(item)

                current_step += 1
                if progress_callback:
                    progress_callback(current_step, total_steps)

            # 第二阶段：临时名 -> 目标新名
            for item in temp_renamed_items:
                temp_p = Path(item['temp_path'])
                new_p = Path(item['new_path'])

                # 如果目标文件已存在（理论上不应该），添加后缀
                if new_p.exists():
                    counter = 1
                    while True:
                        alt_path = new_p.with_name(f"{new_p.stem}_{counter}{new_p.suffix}")
                        if not alt_path.exists():
                            new_p = alt_path
                            break
                        counter += 1

                temp_p.rename(new_p)

                final_history.append({
                    'old_path': item['old_path'],
                    'new_path': str(new_p),
                    'old_name': item['old_name'],
                    'new_name': new_p.name
                })

                current_step += 1
                if progress_callback:
                    progress_callback(current_step, total_steps)

            # 记录到历史
            self.undo_history.append(final_history)
            self.undo_dir = str(Path(preview_list[0]['old_path']).parent)

            # 清空预览数据
            self.preview_data = []

            return True

        except Exception as e:
            # 回滚：把仍然停留在临时名（即阶段二还没处理到）的文件改回原名。
            # 注意：已经在阶段二成功改成目标新名的文件，此时 temp_path 已不存在，
            # 不会被这里误伤——它们保持已改名状态。
            for item in temp_renamed_items:
                temp_p = Path(item['temp_path'])
                old_p = Path(item['old_path'])
                if temp_p.exists():
                    try:
                        temp_p.rename(old_p)
                    except Exception:
                        pass

            # 之前这里直接抛异常，导致 final_history 里已经真正生效的改名
            # 从未写入 undo_history，用户完全没办法撤销这部分已经发生的改动。
            # 现在即使本次操作没有完全成功，也要把已经生效的部分记下来。
            if final_history:
                self.undo_history.append(final_history)
                self.undo_dir = str(Path(preview_list[0]['old_path']).parent)

            raise RuntimeError(
                f"Rename partially failed. {len(final_history)} file(s) were already "
                f"renamed (can be undone) and the rest were rolled back. Error: {str(e)}"
            )

    def undo_rename(self, progress_callback=None) -> bool:
        """
        撤销上一次的批量重命名操作
        """
        if not self.undo_history or not self.undo_dir:
            raise ValueError("msg_no_undo_history")

        # 先只"看"最后一条历史，不要立刻 pop 掉：
        # 只有整个撤销过程全部成功，才真正把它从历史中移除，
        # 避免撤销中途失败时把这条历史记录永久弄丢。
        last_operation = self.undo_history[-1]
        total_steps = len(last_operation) * 2
        current_step = 0
        temp_renamed_items = []

        try:
            # 第一阶段：新名 -> 临时名
            for item in last_operation:
                new_p = Path(item['new_path'])
                old_p = Path(item['old_path'])

                if new_p.exists():
                    temp_name = f"{self.temp_prefix}{old_p.name}"
                    temp_p = new_p.with_name(temp_name)
                    new_p.rename(temp_p)
                    temp_renamed_items.append({
                        'temp_path': temp_p,
                        'target_old_path': old_p,
                        'new_path': new_p,
                        'orig_old_path': item['old_path'],
                        'old_name': item['old_name'],
                        'done': False
                    })

                current_step += 1
                if progress_callback:
                    progress_callback(current_step, total_steps)

            # 第二阶段：临时名 -> 原名
            for item in temp_renamed_items:
                temp_p = item['temp_path']
                old_p = item['target_old_path']

                # 如果原文件已存在（可能被其他文件占用），添加后缀
                if old_p.exists():
                    counter = 1
                    while True:
                        alt_path = old_p.with_name(f"{old_p.stem}_{counter}{old_p.suffix}")
                        if not alt_path.exists():
                            old_p = alt_path
                            break
                        counter += 1

                temp_p.rename(old_p)
                item['done'] = True

                current_step += 1
                if progress_callback:
                    progress_callback(current_step, total_steps)

            # 全部成功，才真正把这条历史记录弹出
            self.undo_history.pop()
            if not self.undo_history:
                self.undo_dir = ""

            return True

        except Exception as e:
            # 回滚：把这次撤销过程中已经改成"临时名"、但还没来得及改回
            # "原名"的文件，重新改回"新名"（即撤销前的状态），
            # 避免磁盘上残留 __temp_rename__ 前缀的文件。
            for item in temp_renamed_items:
                if item['done']:
                    continue
                temp_p = item['temp_path']
                new_p = item['new_path']
                if temp_p.exists():
                    try:
                        temp_p.rename(new_p)
                    except Exception:
                        pass

            # 已经成功撤销的文件，从历史记录里去掉；
            # 还没撤销成功的部分继续保留在历史里，允许用户之后重试撤销，
            # 而不是像之前那样直接把整条历史记录弄丢。
            done_orig_old_paths = {
                item['orig_old_path'] for item in temp_renamed_items if item['done']
            }
            remaining_ops = [
                op for op in last_operation if op['old_path'] not in done_orig_old_paths
            ]

            if remaining_ops:
                self.undo_history[-1] = remaining_ops
            else:
                self.undo_history.pop()
                if not self.undo_history:
                    self.undo_dir = ""

            raise RuntimeError(f"Undo failed: {str(e)}")

    # ============ 清理方法 ============

    def clear_preview_data(self):
        """清空预览数据"""
        self.preview_data = []

    def clear_undo_history(self):
        """清空撤销历史"""
        self.undo_history = []
        self.undo_dir = ""

    def check_and_clean_temp_files(self, directory_path: str) -> list:
        """
        扫描并清理上次程序异常崩溃留下的临时文件
        :return: 已恢复的文件名列表
        """
        dir_path = Path(directory_path)
        recovered_files = []

        if not dir_path.exists():
            return recovered_files

        for file_path in dir_path.iterdir():
            if file_path.is_file() and file_path.name.startswith(self.temp_prefix):
                original_name = file_path.name.replace(self.temp_prefix, "", 1)
                original_path = file_path.with_name(original_name)
                try:
                    if not original_path.exists():
                        file_path.rename(original_path)
                        recovered_files.append(original_name)
                except Exception:
                    pass

        return recovered_files