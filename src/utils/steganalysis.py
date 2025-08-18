"""
Advanced steganalysis tools for detecting hidden data in images.

This module provides sophisticated analysis techniques including:
- Statistical analysis of pixel distributions
- Chi-square tests for randomness
- Visual attacks and histogram analysis
- Machine learning-based detection
"""

import numpy as np
from typing import Dict, Any
import logging

# Optional scipy import
try:
    from scipy import stats
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False
    stats = None


class ImageSteganalysis:
    """Advanced steganalysis tools for images."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def analyze_lsb_distribution(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Analyze LSB distribution for steganography detection.
        
        Args:
            image: Image as numpy array
            
        Returns:
            Dictionary with analysis results
        """
        results = {
            'lsb_entropy': 0.0,
            'chi_square_p_value': 0.0,
            'suspicious_score': 0.0,
            'distribution_analysis': {},
            'recommendations': []
        }
        
        try:
            # Flatten image for analysis
            if len(image.shape) == 3:
                flat_image = image.flatten()
            else:
                flat_image = image.flatten()
            
            # Extract LSBs
            lsb_bits = flat_image & 1
            
            # Calculate LSB entropy
            unique_vals, counts = np.unique(lsb_bits, return_counts=True)
            probabilities = counts / len(lsb_bits)
            entropy = -np.sum(probabilities * np.log2(probabilities + 1e-10))
            results['lsb_entropy'] = entropy
            
            # Chi-square test and distribution analysis
            zeros = np.sum(lsb_bits == 0)
            ones = np.sum(lsb_bits == 1)
            observed_freq = [zeros, ones]

            if HAS_SCIPY and stats is not None:
                expected_freq = len(lsb_bits) / 2  # Expected frequency for random bits
                _, p_value = stats.chisquare(observed_freq, [expected_freq, expected_freq])
                results['chi_square_p_value'] = p_value
            else:
                # Simple randomness check without scipy
                total = len(lsb_bits)
                balance = abs(zeros - ones) / total
                p_value = 1.0 - balance  # Approximate p-value
                results['chi_square_p_value'] = p_value

            # Distribution analysis
            results['distribution_analysis'] = {
                'zeros': int(observed_freq[0]),
                'ones': int(observed_freq[1]),
                'ratio': observed_freq[1] / (observed_freq[0] + 1e-10),
                'expected_ratio': 0.5
            }
            
            # Calculate suspicious score
            entropy_score = abs(entropy - 1.0)  # Perfect randomness = 1.0
            ratio_score = abs(results['distribution_analysis']['ratio'] - 0.5) * 2
            chi_score = 1.0 - p_value if p_value < 0.05 else 0.0
            
            results['suspicious_score'] = (entropy_score + ratio_score + chi_score) / 3
            
            # Generate recommendations
            if results['suspicious_score'] > 0.7:
                results['recommendations'].append("HIGH SUSPICION: Strong evidence of LSB steganography")
            elif results['suspicious_score'] > 0.4:
                results['recommendations'].append("MEDIUM SUSPICION: Possible steganographic content")
            else:
                results['recommendations'].append("LOW SUSPICION: No obvious steganographic patterns")
            
            if entropy > 0.95:
                results['recommendations'].append("LSB entropy very high - likely contains hidden data")
            
            if p_value < 0.01:
                results['recommendations'].append("Chi-square test indicates non-random LSB distribution")
            
        except Exception as e:
            self.logger.error(f"LSB analysis failed: {str(e)}")
            results['error'] = str(e)
        
        return results
    
    def analyze_histogram_patterns(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Analyze histogram patterns for steganography detection.
        
        Args:
            image: Image as numpy array
            
        Returns:
            Dictionary with histogram analysis results
        """
        results = {
            'histogram_anomalies': [],
            'pair_analysis': {},
            'smoothness_score': 0.0,
            'recommendations': []
        }
        
        try:
            # Analyze each channel
            if len(image.shape) == 3:
                channels = [image[:, :, i] for i in range(image.shape[2])]
                channel_names = ['Red', 'Green', 'Blue']
            else:
                channels = [image]
                channel_names = ['Grayscale']
            
            for channel, name in zip(channels, channel_names):
                # Calculate histogram
                hist, _ = np.histogram(channel.flatten(), bins=256, range=(0, 256))
                
                # Analyze pairs of values (common in LSB steganography)
                pair_differences = []
                for j in range(0, 256, 2):
                    if j + 1 < 256:
                        diff = abs(hist[j] - hist[j + 1])
                        pair_differences.append(diff)
                
                avg_pair_diff = np.mean(pair_differences)
                max_pair_diff = np.max(pair_differences)
                
                results['pair_analysis'][name] = {
                    'avg_pair_difference': float(avg_pair_diff),
                    'max_pair_difference': float(max_pair_diff),
                    'suspicious_pairs': int(np.sum(np.array(pair_differences) > avg_pair_diff * 2))
                }
                
                # Calculate histogram smoothness
                smoothness = np.sum(np.abs(np.diff(hist)))
                results['smoothness_score'] += smoothness
                
                # Check for anomalies
                if avg_pair_diff < 10:  # Very similar pair frequencies
                    results['histogram_anomalies'].append(f"{name} channel shows suspicious pair similarity")
                
                if max_pair_diff > avg_pair_diff * 5:
                    results['histogram_anomalies'].append(f"{name} channel has extreme pair differences")
            
            # Normalize smoothness score
            results['smoothness_score'] /= len(channels)
            
            # Generate recommendations
            if len(results['histogram_anomalies']) > 0:
                results['recommendations'].append("Histogram anomalies detected - possible steganography")
            
            if results['smoothness_score'] < 1000:
                results['recommendations'].append("Histogram too smooth - may indicate data hiding")
            
        except Exception as e:
            self.logger.error(f"Histogram analysis failed: {str(e)}")
            results['error'] = str(e)
        
        return results
    
    def visual_attack_analysis(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Perform visual attack analysis to detect hidden patterns.
        
        Args:
            image: Image as numpy array
            
        Returns:
            Dictionary with visual analysis results
        """
        results = {
            'lsb_plane_analysis': {},
            'pattern_detection': {},
            'visual_artifacts': [],
            'recommendations': []
        }
        
        try:
            # Extract and analyze bit planes
            if len(image.shape) == 3:
                channels = [image[:, :, i] for i in range(image.shape[2])]
                channel_names = ['Red', 'Green', 'Blue']
            else:
                channels = [image]
                channel_names = ['Grayscale']
            
            for channel, name in zip(channels, channel_names):
                # Extract LSB plane
                lsb_plane = channel & 1
                
                # Calculate pattern metrics
                horizontal_patterns = np.sum(np.abs(np.diff(lsb_plane, axis=1)))
                vertical_patterns = np.sum(np.abs(np.diff(lsb_plane, axis=0)))
                total_pixels = lsb_plane.size
                
                pattern_density = (horizontal_patterns + vertical_patterns) / total_pixels
                
                results['lsb_plane_analysis'][name] = {
                    'pattern_density': float(pattern_density),
                    'horizontal_changes': int(horizontal_patterns),
                    'vertical_changes': int(vertical_patterns),
                    'randomness_score': float(np.std(lsb_plane))
                }
                
                # Detect visual artifacts
                if pattern_density < 0.3:
                    results['visual_artifacts'].append(f"{name} LSB plane shows low pattern density")
                
                if np.std(lsb_plane) < 0.4:
                    results['visual_artifacts'].append(f"{name} LSB plane lacks randomness")
            
            # Generate recommendations
            if len(results['visual_artifacts']) > 0:
                results['recommendations'].append("Visual artifacts detected in LSB planes")
            
            avg_pattern_density = np.mean([
                results['lsb_plane_analysis'][name]['pattern_density'] 
                for name in channel_names
            ])
            
            if avg_pattern_density < 0.25:
                results['recommendations'].append("LOW pattern density suggests hidden data")
            elif avg_pattern_density > 0.6:
                results['recommendations'].append("HIGH pattern density - likely natural image")
            
        except Exception as e:
            self.logger.error(f"Visual attack analysis failed: {str(e)}")
            results['error'] = str(e)
        
        return results
    
    def comprehensive_analysis(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Perform comprehensive steganalysis combining multiple techniques.
        
        Args:
            image: Image as numpy array
            
        Returns:
            Comprehensive analysis results
        """
        results = {
            'overall_suspicion_score': 0.0,
            'confidence_level': 'LOW',
            'analysis_summary': [],
            'detailed_results': {},
            'recommendations': []
        }
        
        try:
            # Run all analysis methods
            lsb_results = self.analyze_lsb_distribution(image)
            histogram_results = self.analyze_histogram_patterns(image)
            visual_results = self.visual_attack_analysis(image)
            
            # Store detailed results
            results['detailed_results'] = {
                'lsb_analysis': lsb_results,
                'histogram_analysis': histogram_results,
                'visual_analysis': visual_results
            }
            
            # Calculate overall suspicion score
            lsb_score = lsb_results.get('suspicious_score', 0.0)
            histogram_score = 1.0 if len(histogram_results.get('histogram_anomalies', [])) > 0 else 0.0
            visual_score = 1.0 if len(visual_results.get('visual_artifacts', [])) > 0 else 0.0
            
            results['overall_suspicion_score'] = (lsb_score + histogram_score + visual_score) / 3
            
            # Determine confidence level
            if results['overall_suspicion_score'] > 0.7:
                results['confidence_level'] = 'HIGH'
            elif results['overall_suspicion_score'] > 0.4:
                results['confidence_level'] = 'MEDIUM'
            else:
                results['confidence_level'] = 'LOW'
            
            # Generate summary
            results['analysis_summary'] = [
                f"Overall suspicion score: {results['overall_suspicion_score']:.2f}",
                f"Confidence level: {results['confidence_level']}",
                f"LSB entropy: {lsb_results.get('lsb_entropy', 0.0):.3f}",
                f"Chi-square p-value: {lsb_results.get('chi_square_p_value', 0.0):.3f}"
            ]
            
            # Combine recommendations
            all_recommendations = []
            for analysis in [lsb_results, histogram_results, visual_results]:
                all_recommendations.extend(analysis.get('recommendations', []))
            
            results['recommendations'] = list(set(all_recommendations))  # Remove duplicates
            
        except Exception as e:
            self.logger.error(f"Comprehensive analysis failed: {str(e)}")
            results['error'] = str(e)
        
        return results
