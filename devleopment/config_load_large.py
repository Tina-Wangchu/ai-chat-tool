"""
大型项目配置管理模块

功能：
- 支持 YAML 和 JSON 配置文件
- 配置验证和类型检查
- 环境变量替换
- 配置缓存和热重载
- 多配置文件支持（开发/测试/生产环境）
- 日志记录
- 异常处理

使用示例：
    from config_load_large import ConfigManager

    # 初始化配置管理器
    config = ConfigManager('config.yaml', environment='dev')

    # 获取 API 客户端
    client = config.get_client()

    # 获取配置项
    model = config.get('api.model')
    temperature = config.get('model_parameters.temperature', default=0.7)
"""

import os
import json
import yaml
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Union, List
from dataclasses import dataclass, field
from enum import Enum
from openai import OpenAI
from threading import Lock
from datetime import datetime
import copy


class Environment(Enum):
    """环境类型枚举"""
    DEV = "development"
    TEST = "testing"
    PROD = "production"


class ConfigFormat(Enum):
    """配置文件格式枚举"""
    YAML = "yaml"
    JSON = "json"
    AUTO = "auto"


@dataclass
class ConfigSchema:
    """配置架构定义"""
    required_fields: Dict[str, List[str]] = field(default_factory=dict)
    optional_fields: Dict[str, List[str]] = field(default_factory=dict)
    type_checks: Dict[str, type] = field(default_factory=dict)
    value_ranges: Dict[str, tuple] = field(default_factory=dict)


class ConfigValidationError(Exception):
    """配置验证错误"""
    pass


class ConfigLoadError(Exception):
    """配置加载错误"""
    pass


class ConfigManager:
    """
    大型项目配置管理器

    功能：
    - 配置文件加载（YAML/JSON）
    - 配置验证
    - 环境变量替换
    - 配置缓存
    - 热重载
    - 多环境支持
    """

    # 类变量：配置缓存
    _config_cache: Dict[str, Dict[str, Any]] = {}
    _cache_lock = Lock()

    # 默认配置架构
    DEFAULT_SCHEMA = ConfigSchema(
        required_fields={
            'api': ['base_url', 'api_key', 'model'],
            'model_parameters': ['temperature'],
            'stream': ['enabled']
        },
        optional_fields={
            'model_parameters': ['top_p', 'max_tokens', 'presence_penalty', 'frequency_penalty'],
            'thinking': ['enabled', 'budget'],
            'roles': ['default', 'available'],
            'conversation': ['message_count_warning_threshold'],
            'debug': ['verbose', 'log_requests']
        },
        type_checks={
            'api.model': str,
            'model_parameters.temperature': (int, float),
            'model_parameters.max_tokens': int,
            'stream.enabled': bool
        },
        value_ranges={
            'model_parameters.temperature': (0.0, 2.0),
            'model_parameters.top_p': (0.0, 1.0),
            'model_parameters.max_tokens': (1, 32000),
            'model_parameters.presence_penalty': (-2.0, 2.0),
            'model_parameters.frequency_penalty': (-2.0, 2.0)
        }
    )

    def __init__(
        self,
        config_path: Union[str, Path],
        environment: Optional[str] = None,
        schema: Optional[ConfigSchema] = None,
        enable_cache: bool = True,
        auto_reload: bool = False,
        logger: Optional[logging.Logger] = None
    ):
        """
        初始化配置管理器

        Args:
            config_path: 配置文件路径
            environment: 环境名称（dev/test/prod）
            schema: 配置验证架构
            enable_cache: 是否启用缓存
            auto_reload: 是否自动重载配置
            logger: 日志记录器
        """
        self.config_path = Path(config_path)
        self.environment = environment or os.getenv('APP_ENV', 'development')
        self.schema = schema or self.DEFAULT_SCHEMA
        self.enable_cache = enable_cache
        self.auto_reload = auto_reload

        # 初始化日志
        self.logger = logger or self._setup_default_logger()

        # 配置数据
        self._config: Dict[str, Any] = {}
        self._client: Optional[OpenAI] = None

        # 文件修改时间（用于热重载）
        self._last_modified: Optional[float] = None

        # 加载配置
        self._load_config()

        self.logger.info(f"配置管理器初始化完成: {self.config_path}")

    def _setup_default_logger(self) -> logging.Logger:
        """设置默认日志记录器"""
        logger = logging.getLogger('ConfigManager')
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def _load_config(self) -> None:
        """加载配置文件"""
        try:
            # 检查缓存
            if self.enable_cache:
                cache_key = f"{self.config_path}:{self.environment}"
                with self._cache_lock:
                    if cache_key in self._config_cache:
                        self._config = self._config_cache[cache_key]
                        self.logger.debug("使用缓存的配置")
                        return

            # 检测文件格式
            file_format = self._detect_format()

            # 读取文件
            with open(self.config_path, 'r', encoding='utf-8') as f:
                if file_format == ConfigFormat.YAML:
                    raw_config = yaml.safe_load(f)
                elif file_format == ConfigFormat.JSON:
                    raw_config = json.load(f)
                else:
                    raise ConfigLoadError(f"不支持的配置文件格式")

            # 处理环境特定配置
            self._config = self._process_environment_config(raw_config)

            # 替换环境变量
            self._replace_env_variables()

            # 验证配置
            self._validate_config()

            # 更新缓存
            if self.enable_cache:
                with self._cache_lock:
                    cache_key = f"{self.config_path}:{self.environment}"
                    self._config_cache[cache_key] = copy.deepcopy(self._config)

            # 更新文件修改时间
            self._last_modified = self.config_path.stat().st_mtime

            self.logger.info(f"配置加载成功: {self.config_path}")

        except FileNotFoundError:
            raise ConfigLoadError(f"配置文件不存在: {self.config_path}")
        except yaml.YAMLError as e:
            raise ConfigLoadError(f"YAML 解析错误: {str(e)}")
        except json.JSONDecodeError as e:
            raise ConfigLoadError(f"JSON 解析错误: {str(e)}")

    def _detect_format(self) -> ConfigFormat:
        """检测配置文件格式"""
        suffix = self.config_path.suffix.lower()

        format_map = {
            '.yaml': ConfigFormat.YAML,
            '.yml': ConfigFormat.YAML,
            '.json': ConfigFormat.JSON
        }

        return format_map.get(suffix, ConfigFormat.YAML)

    def _process_environment_config(self, raw_config: Dict[str, Any]) -> Dict[str, Any]:
        """处理环境特定配置"""
        # 如果有环境特定配置，合并到主配置
        if 'environments' in raw_config:
            env_config = raw_config['environments'].get(self.environment, {})
            base_config = {k: v for k, v in raw_config.items() if k != 'environments'}
            return self._deep_merge(base_config, env_config)

        return raw_config

    def _deep_merge(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """深度合并字典"""
        result = copy.deepcopy(base)

        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value

        return result

    def _replace_env_variables(self) -> None:
        """替换配置中的环境变量"""
        def replace_value(value: Any) -> Any:
            if isinstance(value, str):
                # 支持 ${VAR_NAME} 格式
                if value.startswith('${') and value.endswith('}'):
                    env_var = value[2:-1]
                    env_value = os.getenv(env_var)
                    if env_value is None:
                        self.logger.warning(f"环境变量未定义: {env_var}")
                    return env_value or value
                return value
            elif isinstance(value, dict):
                return {k: replace_value(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [replace_value(item) for item in value]
            return value

        self._config = replace_value(self._config)

    def _validate_config(self) -> None:
        """验证配置完整性"""
        errors = []

        # 检查必需字段
        for section, fields in self.schema.required_fields.items():
            if section not in self._config:
                errors.append(f"缺少配置节: {section}")
                continue

            for field in fields:
                if field not in self._config[section]:
                    errors.append(f"缺少配置项: {section}.{field}")

        # 类型检查
        for path, expected_type in self.schema.type_checks.items():
            try:
                value = self._get_nested_value(path)
                if not isinstance(value, expected_type):
                    errors.append(
                        f"类型错误: {path} 期望 {expected_type}，实际 {type(value)}"
                    )
            except KeyError:
                pass  # 必需字段已在上面检查

        # 值范围检查
        for path, (min_val, max_val) in self.schema.value_ranges.items():
            try:
                value = self._get_nested_value(path)
                if not (min_val <= value <= max_val):
                    errors.append(
                        f"值超出范围: {path}={value}，应在 [{min_val}, {max_val}]"
                    )
            except (KeyError, TypeError):
                pass

        if errors:
            error_msg = "配置验证失败:\n" + "\n".join(f"  - {e}" for e in errors)
            self.logger.error(error_msg)
            raise ConfigValidationError(error_msg)

        self.logger.debug("配置验证通过")

    def _get_nested_value(self, path: str) -> Any:
        """获取嵌套配置值"""
        keys = path.split('.')
        value = self._config

        for key in keys:
            if isinstance(value, dict):
                value = value[key]
            else:
                raise KeyError(f"路径不存在: {path}")

        return value

    def get(self, path: str, default: Any = None) -> Any:
        """
        获取配置项

        Args:
            path: 配置路径，如 'api.model'
            default: 默认值

        Returns:
            配置值或默认值
        """
        try:
            # 检查是否需要热重载
            if self.auto_reload:
                current_mtime = self.config_path.stat().st_mtime
                if current_mtime != self._last_modified:
                    self.logger.info("检测到配置文件变更，重新加载...")
                    self._load_config()

            return self._get_nested_value(path)
        except KeyError:
            if default is not None:
                return default
            raise

    def get_all(self) -> Dict[str, Any]:
        """获取所有配置"""
        return copy.deepcopy(self._config)

    def get_client(self) -> OpenAI:
        """
        获取配置的 API 客户端

        Returns:
            OpenAI 客户端实例
        """
        if self._client is None:
            api_key = self.get('api.api_key')
            base_url = self.get('api.base_url')

            if not api_key:
                raise ConfigLoadError("未配置 api_key")

            self._client = OpenAI(
                api_key=api_key,
                base_url=base_url
            )
            self.logger.info("API 客户端创建成功")

        return self._client

    def get_role(self, role_id: str) -> Optional[Dict[str, Any]]:
        """
        获取角色配置

        Args:
            role_id: 角色 ID

        Returns:
            角色配置字典，未找到返回 None
        """
        roles = self.get('roles.available', [])
        for role in roles:
            if role.get('id') == role_id:
                return role
        return None

    def get_default_role(self) -> Dict[str, Any]:
        """获取默认角色配置"""
        default_id = self.get('roles.default', '3')
        role = self.get_role(default_id)
        if role:
            return role
        # 返回 AI 助手作为后备
        return {
            'id': '3',
            'name': 'AI助手',
            'system_prompt': '你是一个友好的AI助手。'
        }

    def reload(self) -> None:
        """强制重新加载配置"""
        self.logger.info("强制重新加载配置...")

        # 清除缓存
        if self.enable_cache:
            cache_key = f"{self.config_path}:{self.environment}"
            with self._cache_lock:
                self._config_cache.pop(cache_key, None)

        # 重新加载
        self._load_config()

        # 重置客户端
        self._client = None

        self.logger.info("配置重新加载完成")

    def update(self, path: str, value: Any) -> None:
        """
        更新配置项（不持久化）

        Args:
            path: 配置路径
            value: 新值
        """
        keys = path.split('.')
        config = self._config

        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]

        config[keys[-1]] = value
        self.logger.debug(f"配置已更新: {path} = {value}")

    def export(self, export_path: Union[str, Path], format: str = 'yaml') -> None:
        """
        导出当前配置

        Args:
            export_path: 导出文件路径
            format: 导出格式（yaml/json）
        """
        export_path = Path(export_path)

        with open(export_path, 'w', encoding='utf-8') as f:
            if format == 'yaml':
                yaml.dump(self._config, f, allow_unicode=True, default_flow_style=False)
            elif format == 'json':
                json.dump(self._config, f, ensure_ascii=False, indent=2)
            else:
                raise ValueError(f"不支持的导出格式: {format}")

        self.logger.info(f"配置已导出到: {export_path}")

    def __repr__(self) -> str:
        return f"ConfigManager(path={self.config_path}, env={self.environment})"


# 工厂函数
def create_config_manager(
    config_path: str = 'config.yaml',
    environment: Optional[str] = None,
    **kwargs
) -> ConfigManager:
    """
    创建配置管理器的工厂函数

    Args:
        config_path: 配置文件路径
        environment: 环境名称
        **kwargs: 其他 ConfigManager 参数

    Returns:
        ConfigManager 实例
    """
    return ConfigManager(config_path, environment, **kwargs)


# 单例模式的全局配置管理器
_global_config: Optional[ConfigManager] = None


def get_global_config() -> ConfigManager:
    """获取全局配置管理器（单例模式）"""
    global _global_config
    if _global_config is None:
        _global_config = ConfigManager('config.yaml')
    return _global_config


# 使用示例
if __name__ == '__main__':
    # 基本使用
    print("=" * 60)
    print("配置管理器使用示例")
    print("=" * 60)

    try:
        # 创建配置管理器
        config = ConfigManager('config.yaml', environment='development')

        # 获取配置项
        print(f"\n1. 模型名称: {config.get('api.model')}")
        print(f"2. 温度参数: {config.get('model_parameters.temperature')}")
        print(f"3. 流式输出: {config.get('stream.enabled')}")

        # 获取 API 客户端
        client = config.get_client()
        print(f"\n4. API 客户端: {client}")

        # 获取角色配置
        role = config.get_default_role()
        print(f"\n5. 默认角色: {role.get('name')}")

        # 导出配置
        config.export('config_export.json', format='json')
        print(f"\n6. 配置已导出到 config_export.json")

    except (ConfigLoadError, ConfigValidationError) as e:
        print(f"\n错误: {str(e)}")
