"""
LLM Provider interface and implementations
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, AsyncGenerator
import logging

logger = logging.getLogger(__name__)


class LLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    @abstractmethod
    async def generate(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a response from the LLM"""
        pass
    
    @abstractmethod
    async def stream(self, prompt: str, context: Dict[str, Any]) -> AsyncGenerator[str, None]:
        """Stream a response from the LLM"""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the provider is healthy"""
        pass


class MockLLMProvider(LLMProvider):
    """Mock LLM provider for demo/testing"""
    
    def __init__(self):
        self.responses = {
            'rsa': (
                'RSA-2048 is flagged because the asset is used for digital signatures '
                'and belongs to an asymmetric cryptographic family affected by quantum '
                'algorithms (Shor\'s algorithm). The associated payment service also has '
                'a long data-security lifetime, increasing migration urgency.'
            ),
            'quantum': (
                'Quantum-vulnerable assets in this project: RSA-2048 (digital signatures, '
                'key transport), ECDSA P-256 (signatures, authentication), ECDH P-256 '
                '(key establishment). These are all vulnerable to Shor\'s algorithm which '
                'can break asymmetric cryptography on a sufficiently large quantum computer.'
            ),
            'migration': (
                'For RSA-2048 digital signatures, the recommended migration path is '
                'ML-DSA-65 (Dilithium) with a hybrid option of RSA-2048 + ML-DSA-65. '
                'For ECDH P-256 key establishment, ML-KEM-768 (Kyber) is recommended '
                'with hybrid ECDH + ML-KEM. Migration complexity is Medium for signatures, '
                'High for key establishment.'
            ),
            'default': (
                'Based on the ECDAT findings, I can explain the risk assessments and '
                'migration recommendations. The deterministic engines have classified '
                'assets based on algorithm type, key parameters, usage context, and '
                'business criticality. What specific finding would you like me to elaborate on?'
            ),
        }
    
    async def generate(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a mock response based on the prompt"""
        prompt_lower = prompt.lower()
        
        if 'rsa' in prompt_lower or '2048' in prompt_lower:
            text = self.responses['rsa']
        elif 'quantum' in prompt_lower or 'vulnerab' in prompt_lower:
            text = self.responses['quantum']
        elif 'migrat' in prompt_lower or 'hybrid' in prompt_lower or 'pqc' in prompt_lower:
            text = self.responses['migration']
        else:
            text = self.responses['default']
        
        return {
            'text': text,
            'sources': self._get_sources(prompt_lower),
            'confidence': 0.95,
        }
    
    def _get_sources(self, prompt: str) -> list:
        """Return mock sources based on prompt"""
        if 'rsa' in prompt or '2048' in prompt:
            return [
                {'title': 'Finding: RSA-2048 Digital Signature', 'content': 'Algorithm: RSA, Key Size: 2048, Purpose: digital_signature, Risk: HIGH', 'finding_id': 'finding-001'},
                {'title': 'Risk Assessment: RSA-2048', 'content': 'Risk Level: HIGH, Reasons: Quantum-vulnerable asymmetric algorithm, Critical application, Long data lifetime', 'finding_id': 'finding-001'},
            ]
        elif 'quantum' in prompt or 'vulnerab' in prompt:
            return [
                {'title': 'Quantum Risk Summary', 'content': '423 quantum-vulnerable assets across 3 algorithm families', 'finding_id': 'summary'},
            ]
        elif 'migrat' in prompt or 'hybrid' in prompt or 'pqc' in prompt:
            return [
                {'title': 'Migration Recommendation: RSA-2048', 'content': 'Candidate: ML-DSA-65, Hybrid: RSA-2048 + ML-DSA-65, Complexity: Medium', 'finding_id': 'rec-001'},
                {'title': 'Migration Recommendation: ECDH P-256', 'content': 'Candidate: ML-KEM-768, Hybrid: ECDH + ML-KEM-768, Complexity: High', 'finding_id': 'rec-002'},
            ]
        return [
            {'title': 'Project: Acme Payments Platform', 'content': '4 high-risk findings, 12 medium-risk, 23 low-risk', 'finding_id': 'project-summary'},
        ]
    
    async def stream(self, prompt: str, context: Dict[str, Any]) -> AsyncGenerator[str, None]:
        """Stream mock response"""
        result = await self.generate(prompt, context)
        words = result['text'].split()
        for word in words:
            yield word + ' '
    
    async def health_check(self) -> bool:
        return True


class OpenAICompatibleProvider(LLMProvider):
    """OpenAI-compatible API provider"""
    
    def __init__(self, base_url: str, api_key: str, model: str):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.model = model
    
    async def generate(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate response via OpenAI-compatible API"""
        import httpx
        
        system_prompt = self._build_system_prompt(context)
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f'{self.base_url}/chat/completions',
                headers={
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json',
                },
                json={
                    'model': self.model,
                    'messages': [
                        {'role': 'system', 'content': system_prompt},
                        {'role': 'user', 'content': prompt},
                    ],
                    'temperature': 0.3,
                    'max_tokens': 1000,
                },
            )
            response.raise_for_status()
            data = response.json()
            
            return {
                'text': data['choices'][0]['message']['content'],
                'sources': [],  # Sources would be added by the context builder
                'confidence': 0.8,
            }
    
    async def stream(self, prompt: str, context: Dict[str, Any]) -> AsyncGenerator[str, None]:
        """Stream response via OpenAI-compatible API"""
        import httpx
        
        system_prompt = self._build_system_prompt(context)
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream(
                'POST',
                f'{self.base_url}/chat/completions',
                headers={
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json',
                },
                json={
                    'model': self.model,
                    'messages': [
                        {'role': 'system', 'content': system_prompt},
                        {'role': 'user', 'content': prompt},
                    ],
                    'temperature': 0.3,
                    'max_tokens': 1000,
                    'stream': True,
                },
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith('data: '):
                        data_str = line[6:]
                        if data_str == '[DONE]':
                            break
                        try:
                            import json
                            data = json.loads(data_str)
                            if data['choices'][0]['delta'].get('content'):
                                yield data['choices'][0]['delta']['content']
                        except:
                            pass
    
    async def health_check(self) -> bool:
        import httpx
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f'{self.base_url}/models',
                    headers={'Authorization': f'Bearer {self.api_key}'},
                )
                return response.status_code == 200
        except:
            return False
    
    def _build_system_prompt(self, context: Dict[str, Any]) -> str:
        """Build system prompt with context"""
        return (
            "You are an AI assistant for ECDAT, a Cryptographic Discovery & Quantum Readiness Platform. "
            "You explain findings, risk assessments, and migration recommendations generated by deterministic engines. "
            "Never make up findings or risk scores. Only explain what the deterministic engines have produced.\n\n"
            f"Context: {context}"
        )


class LLMProviderFactory:
    """Factory for creating LLM providers"""
    
    _providers: Dict[str, type] = {
        'mock': MockLLMProvider,
        'openai_compatible': OpenAICompatibleProvider,
    }
    
    @classmethod
    def get_provider(cls, provider_type: str = 'mock', **kwargs) -> LLMProvider:
        """Get an LLM provider instance"""
        if provider_type not in cls._providers:
            raise ValueError(f"Unknown provider type: {provider_type}")
        
        provider_class = cls._providers[provider_type]
        return provider_class(**kwargs)
    
    @classmethod
    def register_provider(cls, name: str, provider_class: type):
        """Register a new provider"""
        cls._providers[name] = provider_class