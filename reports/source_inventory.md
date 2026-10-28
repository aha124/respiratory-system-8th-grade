# Source inventory

Every node in `models/respiratory.glb`. "Quad share" is the fraction of four-sided faces in the source object. BodyParts3D meshes are triangle meshes, so a high quad share suggests the surface was modeled or retopologized by Z-Anatomy artists on the BodyParts3D body rather than taken over unchanged. This is a hint, not proof.

| Node | Group | Source file | Source object(s) | FMA ID (from BodyParts3D lists) | Source verts | Exported tris | Max simplification error | Quad share |
|---|---|---|---|---|---|---|---|---|
| nasal_cavity | airway | VisceralSystem100.fbx | Mucosa of nasal cavity | n/a | 4860 | 2530 | 0.496 mm (limit 1) | 1.00 |
| inferior_nasal_conchae | airway | SkeletalSystem100.fbx | Inferior nasal concha bone.r, Inferior nasal concha bone.l | FMA54736 | 476 | 622 | 0.321 mm (limit 1) | 0.00 |
| ethmoid_bone | airway | SkeletalSystem100.fbx | Ethmoid bone, Posterior cells of ethmoid bone.l, Middle cells of ethmoid bone.l, Anterior cells of ethmoid bone.l (+3 more) | FMA52740 | 8022 | 5329 | 0.44 mm (limit 1) | 0.66 |
| nasopharynx | airway | VisceralSystem100.fbx | Nasopharynx | n/a | 978 | 782 | 0.317 mm (limit 1) | 1.00 |
| oropharynx | airway | VisceralSystem100.fbx | Oropharynx | n/a | 1274 | 1036 | 0.384 mm (limit 1) | 1.00 |
| laryngopharynx | airway | VisceralSystem100.fbx | Laryngopharynx | n/a | 1238 | 766 | 0.408 mm (limit 1) | 1.00 |
| epiglottis | airway | VisceralSystem100.fbx | Epiglottis | FMA55130 | 1650 | 332 | 0.399 mm (limit 1) | 0.01 |
| thyroid_cartilage | airway | SkeletalSystem100.fbx | Thyroid cartilage | FMA55099 | 2247 | 892 | 0.366 mm (limit 1) | 0.00 |
| cricoid_cartilage | airway | SkeletalSystem100.fbx | Cricoid cartilage | FMA9615 | 941 | 375 | 0.318 mm (limit 1) | 0.04 |
| arytenoid_cartilages | airway | SkeletalSystem100.fbx | Arytenoid cartilage.r, Arytenoid cartilage.l | FMA55109 | 3784 | 182 | 0.451 mm (limit 1) | 1.00 |
| corniculate_cartilages | airway | SkeletalSystem100.fbx | Corniculate cartilage.r, Corniculate cartilage.l | FMA55110 | 140 | 36 | 0.186 mm (limit 1) | 0.00 |
| vocal_folds | airway | BodyParts3D 4.0 isa_BP3D_4.0_obj_99.zip: FJ2805.obj, FJ2787.obj, FJ2806.obj, FJ2788.obj | right vocal ligament, left vocal ligament, right vocalis, left vocalis | FMA55245, FMA55246, FMA46592, FMA46593 | 5264 | 222 | 0.302 mm (limit 1) | 0.00 |
| trachea | airway | VisceralSystem100.fbx | Trachea | FMA7394 | 2400 | 2372 | 0.346 mm (limit 1) | 0.05 |
| right_main_bronchus | airway | VisceralSystem100.fbx | Right main bronchus | FMA7395 | 156 | 30 | 0.216 mm (limit 1) | 1.00 |
| left_main_bronchus | airway | VisceralSystem100.fbx | Left main bronchus | FMA7396 | 300 | 86 | 0.341 mm (limit 1) | 1.00 |
| intermediate_bronchus | airway | VisceralSystem100.fbx | Intermediate bronchus.r | n/a | 156 | 44 | 0.322 mm (limit 1) | 1.00 |
| right_upper_lobar_bronchus | airway | VisceralSystem100.fbx | Right superior lobar bronchus | n/a | 156 | 44 | 0.422 mm (limit 1) | 1.00 |
| right_middle_lobar_bronchus | airway | VisceralSystem100.fbx | Middle lobar bronchus.r | n/a | 156 | 30 | 0.257 mm (limit 1) | 1.00 |
| right_lower_lobar_bronchus | airway | VisceralSystem100.fbx | Right inferior lobar bronchus | n/a | 588 | 168 | 0.461 mm (limit 1) | 1.00 |
| left_upper_lobar_bronchus | airway | VisceralSystem100.fbx | Left superior lobar bronchus | n/a | 600 | 222 | 0.326 mm (limit 1) | 1.00 |
| left_lower_lobar_bronchus | airway | VisceralSystem100.fbx | Left inferior lobar bronchus | n/a | 444 | 144 | 0.294 mm (limit 1) | 1.00 |
| seg_right_upper_b1 | airway | VisceralSystem100.fbx | Apical segmental bronchus of right lung (BI) | FMA68211 | 3408 | 704 | 0.424 mm (limit 1) | 1.00 |
| seg_right_upper_b2 | airway | VisceralSystem100.fbx | Posterior segmental bronchus of right lung (BII) | FMA68213 | 2520 | 650 | 0.398 mm (limit 1) | 1.00 |
| seg_right_upper_b3 | airway | VisceralSystem100.fbx | Anterior segmental bronchus of right lung (BIII) | FMA68212 | 2532 | 676 | 0.478 mm (limit 1) | 1.00 |
| seg_right_middle_b4 | airway | VisceralSystem100.fbx | Lateral segmental bronchus of right lung (BIV) | FMA68215 | 1632 | 352 | 0.367 mm (limit 1) | 1.00 |
| seg_right_middle_b5 | airway | VisceralSystem100.fbx | Medial segmental bronchus of right lung (BV) | FMA68214 | 1632 | 464 | 0.485 mm (limit 1) | 1.00 |
| seg_right_lower_b6 | airway | VisceralSystem100.fbx | Superior segmental bronchus of right lung (BVI) | FMA68216 | 4572 | 986 | 0.376 mm (limit 1) | 1.00 |
| seg_right_lower_b7 | airway | VisceralSystem100.fbx | Medial basal segmental bronchus of right lung (BVII) | FMA68218 | 888 | 230 | 0.349 mm (limit 1) | 1.00 |
| seg_right_lower_b8 | airway | VisceralSystem100.fbx | Anterior basal segmental bronchus of right lung (BVIII) | FMA68321 | 1476 | 366 | 0.47 mm (limit 1) | 1.00 |
| seg_right_lower_b9 | airway | VisceralSystem100.fbx | Lateral basal segmental bronchus of right lung (BIX) | FMA68220 | 2352 | 476 | 0.35 mm (limit 1) | 1.00 |
| seg_right_lower_b10 | airway | VisceralSystem100.fbx | Posterior basal segmental bronchus of right lung (BX) | FMA68221 | 2208 | 492 | 0.459 mm (limit 1) | 1.00 |
| seg_left_upper_b1_2 | airway | VisceralSystem100.fbx | Apicoposterior segmental bronchus of left lung (BI+BII) | n/a | 3852 | 928 | 0.396 mm (limit 1) | 1.00 |
| seg_left_upper_b3 | airway | VisceralSystem100.fbx | Anterior segmental bronchus of left lung (BIII) | FMA68222 | 1788 | 432 | 0.576 mm (limit 1) | 1.00 |
| seg_left_upper_b4 | airway | VisceralSystem100.fbx | Superior lingular segmental bronchus of left lung (BIV) | FMA68226 | 1044 | 446 | 0.324 mm (limit 1) | 1.00 |
| seg_left_upper_b5 | airway | VisceralSystem100.fbx | Inferior lingular segmental bronchus of left lung (BV) | FMA68227 | 1044 | 340 | 0.364 mm (limit 1) | 1.00 |
| seg_left_lower_b6 | airway | VisceralSystem100.fbx | Superior segmental bronchus of left lung (BVI) | FMA68228 | 2232 | 730 | 0.354 mm (limit 1) | 1.00 |
| seg_left_lower_b7 | airway | VisceralSystem100.fbx | Medial basal segmental bronchus of left lung (BVII) | FMA68230 | 2940 | 690 | 0.454 mm (limit 1) | 1.00 |
| seg_left_lower_b8 | airway | VisceralSystem100.fbx | Anterior basal segmental bronchus of left lung (BVIII) | FMA68231 | 744 | 244 | 0.343 mm (limit 1) | 1.00 |
| seg_left_lower_b9 | airway | VisceralSystem100.fbx | Lateral basal segmental bronchus of left lung (BIX) | FMA68232 | 1176 | 396 | 0.357 mm (limit 1) | 1.00 |
| seg_left_lower_b10 | airway | VisceralSystem100.fbx | Posterior basal segmental bronchus of left lung (BX) | FMA68233 | 588 | 194 | 0.309 mm (limit 1) | 1.00 |
| right_upper_lobe | lungs | VisceralSystem100.fbx | Superior lobe of right lung | FMA7333 | 3902 | 1128 | 0.854 mm (limit 2) | 1.00 |
| right_middle_lobe | lungs | VisceralSystem100.fbx | Middle lobe of right lung | FMA7383 | 3708 | 800 | 0.757 mm (limit 2) | 1.00 |
| right_lower_lobe | lungs | VisceralSystem100.fbx | Inferior lobe of right lung | FMA7337 | 4231 | 1328 | 0.905 mm (limit 2) | 1.00 |
| left_upper_lobe | lungs | VisceralSystem100.fbx | Superior lobe of left lung | FMA7370 | 4662 | 1580 | 0.677 mm (limit 2) | 1.00 |
| left_lower_lobe | lungs | VisceralSystem100.fbx | Inferior lobe of left lung | FMA7371 | 4637 | 1486 | 0.796 mm (limit 2) | 1.00 |
| diaphragm | diaphragm | MuscularSystem100.fbx | Diaphragm | FMA13295 | 19437 | 4190 | 0.908 mm (limit 2) | 1.00 |
| rib_right_1 | skeleton | SkeletalSystem100.fbx | First rib.r | FMA7857 | 1607 | 300 | 0.662 mm (limit 2) | 0.00 |
| rib_left_1 | skeleton | SkeletalSystem100.fbx | First rib.l | FMA7987 | 1607 | 294 | 0.815 mm (limit 2) | 0.00 |
| rib_right_2 | skeleton | SkeletalSystem100.fbx | Second rib.r | FMA7882 | 2684 | 480 | 0.639 mm (limit 2) | 0.00 |
| rib_left_2 | skeleton | SkeletalSystem100.fbx | Second rib.l | FMA8012 | 2684 | 454 | 0.777 mm (limit 2) | 0.00 |
| rib_right_3 | skeleton | SkeletalSystem100.fbx | Third rib.r | FMA7909 | 3492 | 550 | 0.763 mm (limit 2) | 0.00 |
| rib_left_3 | skeleton | SkeletalSystem100.fbx | Third rib.l | FMA8039 | 3492 | 534 | 0.816 mm (limit 2) | 0.00 |
| rib_right_4 | skeleton | SkeletalSystem100.fbx | Fourth rib.r | FMA7957 | 4325 | 602 | 0.864 mm (limit 2) | 0.00 |
| rib_left_4 | skeleton | SkeletalSystem100.fbx | Fourth rib.l | FMA8148 | 4325 | 602 | 0.775 mm (limit 2) | 0.00 |
| rib_right_5 | skeleton | SkeletalSystem100.fbx | Fifth rib.r | FMA8066 | 4690 | 584 | 0.851 mm (limit 2) | 0.00 |
| rib_left_5 | skeleton | SkeletalSystem100.fbx | Fifth rib.l | FMA8093 | 4690 | 560 | 0.695 mm (limit 2) | 0.00 |
| rib_right_6 | skeleton | SkeletalSystem100.fbx | Sixth rib.r | FMA8175 | 5078 | 612 | 0.547 mm (limit 2) | 0.00 |
| rib_left_6 | skeleton | SkeletalSystem100.fbx | Sixth rib.l | FMA8202 | 5078 | 642 | 0.631 mm (limit 2) | 0.00 |
| rib_right_7 | skeleton | SkeletalSystem100.fbx | Seventh rib.r | FMA8229 | 4890 | 628 | 0.847 mm (limit 2) | 0.00 |
| rib_left_7 | skeleton | SkeletalSystem100.fbx | Seventh rib.l | FMA8256 | 4890 | 656 | 0.682 mm (limit 2) | 0.00 |
| rib_right_8 | skeleton | SkeletalSystem100.fbx | Eighth rib.r | FMA8283 | 4137 | 588 | 0.71 mm (limit 2) | 0.00 |
| rib_left_8 | skeleton | SkeletalSystem100.fbx | Eighth rib.l | FMA8310 | 4137 | 576 | 0.769 mm (limit 2) | 0.00 |
| rib_right_9 | skeleton | SkeletalSystem100.fbx | Ninth rib.r | FMA8364 | 3891 | 530 | 0.665 mm (limit 2) | 0.00 |
| rib_left_9 | skeleton | SkeletalSystem100.fbx | Ninth rib.l | FMA8391 | 3891 | 518 | 0.69 mm (limit 2) | 0.00 |
| rib_right_10 | skeleton | SkeletalSystem100.fbx | Tenth rib.r | FMA8445 | 3515 | 442 | 0.82 mm (limit 2) | 0.00 |
| rib_left_10 | skeleton | SkeletalSystem100.fbx | Tenth rib.l | FMA8472 | 3515 | 452 | 0.689 mm (limit 2) | 0.00 |
| rib_right_11 | skeleton | SkeletalSystem100.fbx | Eleventh rib.r | FMA8531 | 2519 | 408 | 0.626 mm (limit 2) | 0.00 |
| rib_left_11 | skeleton | SkeletalSystem100.fbx | Eleventh rib.l | FMA8532 | 2519 | 402 | 0.69 mm (limit 2) | 0.00 |
| rib_right_12 | skeleton | SkeletalSystem100.fbx | Twelfth rib.r | FMA8533 | 1503 | 316 | 0.674 mm (limit 2) | 0.00 |
| rib_left_12 | skeleton | SkeletalSystem100.fbx | Twelfth rib.l | FMA8534 | 1503 | 312 | 0.656 mm (limit 2) | 0.00 |
| costal_cartilage_right_1 | skeleton | SkeletalSystem100.fbx | Costal cartilage of first rib.r | FMA7875 | 1388 | 94 | 0.846 mm (limit 2) | 1.00 |
| costal_cartilage_left_1 | skeleton | SkeletalSystem100.fbx | Costal cartilage of first rib.l | FMA8005 | 1388 | 106 | 0.673 mm (limit 2) | 1.00 |
| costal_cartilage_right_2 | skeleton | SkeletalSystem100.fbx | Costal cartilage of second rib.r | FMA7886 | 1706 | 116 | 0.561 mm (limit 2) | 1.00 |
| costal_cartilage_left_2 | skeleton | SkeletalSystem100.fbx | Costal cartilage of second rib.l | FMA8031 | 1706 | 114 | 0.625 mm (limit 2) | 1.00 |
| costal_cartilage_right_3 | skeleton | SkeletalSystem100.fbx | Costal cartilage of third rib.r | FMA7913 | 1802 | 114 | 0.552 mm (limit 2) | 1.00 |
| costal_cartilage_left_3 | skeleton | SkeletalSystem100.fbx | Costal cartilage of third rib.l | FMA8058 | 1802 | 110 | 0.537 mm (limit 2) | 1.00 |
| costal_cartilage_right_4 | skeleton | SkeletalSystem100.fbx | Costal cartilage of fourth rib.r | FMA7976 | 2238 | 154 | 0.683 mm (limit 2) | 1.00 |
| costal_cartilage_left_4 | skeleton | SkeletalSystem100.fbx | Costal cartilage of fourth rib.l | FMA8167 | 2238 | 150 | 0.747 mm (limit 2) | 1.00 |
| costal_cartilage_right_5 | skeleton | SkeletalSystem100.fbx | Costal cartilage of fifth rib.r | FMA8070 | 3248 | 166 | 0.794 mm (limit 2) | 1.00 |
| costal_cartilage_left_5 | skeleton | SkeletalSystem100.fbx | Costal cartilage of fifth rib.l | FMA8112 | 3248 | 150 | 0.792 mm (limit 2) | 1.00 |
| costal_cartilage_right_6 | skeleton | SkeletalSystem100.fbx | Costal cartilage of sixth rib.r | FMA8194 | 4062 | 224 | 1.126 mm (limit 2) | 1.00 |
| costal_cartilage_left_6 | skeleton | SkeletalSystem100.fbx | Costal cartilage of sixth rib.l | FMA8221 | 4062 | 190 | 1.156 mm (limit 2) | 1.00 |
| costal_cartilage_right_7 | skeleton | SkeletalSystem100.fbx | Costal cartilage of seventh rib.r | FMA8248 | 6884 | 316 | 0.848 mm (limit 2) | 1.00 |
| costal_cartilage_left_7 | skeleton | SkeletalSystem100.fbx | Costal cartilage of seventh rib.l | FMA8275 | 6884 | 344 | 0.729 mm (limit 2) | 1.00 |
| costal_cartilage_right_8 | skeleton | SkeletalSystem100.fbx | Costal cartilage of eighth rib.r | n/a | 1314 | 278 | 0.748 mm (limit 2) | 1.00 |
| costal_cartilage_left_8 | skeleton | SkeletalSystem100.fbx | Costal cartilage of eighth rib.l | n/a | 1314 | 280 | 0.727 mm (limit 2) | 1.00 |
| costal_cartilage_right_9 | skeleton | SkeletalSystem100.fbx | Costal cartilage of ninth rib.r | n/a | 984 | 248 | 0.681 mm (limit 2) | 1.00 |
| costal_cartilage_left_9 | skeleton | SkeletalSystem100.fbx | Costal cartilage of ninth rib.l | n/a | 984 | 246 | 1.137 mm (limit 2) | 1.00 |
| costal_cartilage_right_10 | skeleton | SkeletalSystem100.fbx | Costal cartilage of tenth rib.r | n/a | 764 | 186 | 0.723 mm (limit 2) | 1.00 |
| costal_cartilage_left_10 | skeleton | SkeletalSystem100.fbx | Costal cartilage of tenth rib.l | n/a | 764 | 196 | 0.558 mm (limit 2) | 1.00 |
| sternum | skeleton | SkeletalSystem100.fbx | Manubrium of sternum, Body of sternum, Xiphoid process | FMA7485 | 4035 | 1885 | 0.727 mm (limit 2) | 0.00 |
| clavicle_right | skeleton | SkeletalSystem100.fbx | Clavicle.r | FMA13322 | 789 | 580 | 0.536 mm (limit 2) | 0.00 |
| clavicle_left | skeleton | SkeletalSystem100.fbx | Clavicle.l | FMA13323 | 789 | 570 | 0.58 mm (limit 2) | 0.00 |
| vertebra_t1 | skeleton | SkeletalSystem100.fbx | Vertebra T1 | FMA9165 | 973 | 764 | 0.647 mm (limit 2) | 0.00 |
| vertebra_t2 | skeleton | SkeletalSystem100.fbx | Vertebra T2 | FMA9187 | 1071 | 784 | 0.697 mm (limit 2) | 0.01 |
| vertebra_t3 | skeleton | SkeletalSystem100.fbx | Vertebra T3 | FMA9209 | 1172 | 774 | 0.795 mm (limit 2) | 0.00 |
| vertebra_t4 | skeleton | SkeletalSystem100.fbx | Vertebra T4 | FMA9248 | 1108 | 842 | 0.539 mm (limit 2) | 0.00 |
| vertebra_t5 | skeleton | SkeletalSystem100.fbx | Vertebra T5 | FMA9922 | 1076 | 814 | 0.736 mm (limit 2) | 0.00 |
| vertebra_t6 | skeleton | SkeletalSystem100.fbx | Vertebra T6 | FMA9945 | 890 | 832 | 0.623 mm (limit 2) | 0.00 |
| vertebra_t7 | skeleton | SkeletalSystem100.fbx | Vertebra T7 | FMA9968 | 1397 | 956 | 0.574 mm (limit 2) | 0.06 |
| vertebra_t8 | skeleton | SkeletalSystem100.fbx | Vertebra T8 | FMA9991 | 868 | 819 | 0.523 mm (limit 2) | 0.01 |
| vertebra_t9 | skeleton | SkeletalSystem100.fbx | Vertebra T9 | FMA10014 | 1489 | 1036 | 0.712 mm (limit 2) | 0.00 |
| vertebra_t10 | skeleton | SkeletalSystem100.fbx | Vertebra T10 | FMA10037 | 1529 | 1138 | 0.598 mm (limit 2) | 0.04 |
| vertebra_t11 | skeleton | SkeletalSystem100.fbx | Vertebra T11 | FMA10059 | 899 | 812 | 0.674 mm (limit 2) | 0.01 |
| vertebra_t12 | skeleton | SkeletalSystem100.fbx | Vertebra T12 | FMA10081 | 1293 | 1052 | 0.694 mm (limit 2) | 0.05 |
| heart | heart | CardioVascular41.fbx | Right atrium, Right ventricle, Left atrium, Left ventricle | FMA7088 | 15292 | 5244 | 0.903 mm (limit 2) | 0.00 |
| aorta | heart | CardioVascular41.fbx | Ascending aorta, Aortic arch, Thoracic aorta | FMA3734 | 449 | 768 | 0.241 mm (limit 1) | 0.00 |
| pulmonary_trunk | heart | CardioVascular41.fbx | Pulmonary trunk, Bifurcation of pulmonary trunk | FMA8612 | 321 | 269 | 0.271 mm (limit 1) | 0.00 |
| right_pulmonary_artery | heart | CardioVascular41.fbx | Right pulmonary artery, Apical segmental artery of right lung, Anterior segmental artery of right lung, Posterior segmental artery of right lung (+10 more) | FMA50872 | 9606 | 5712 | 0.324 mm (limit 1) | 0.00 |
| left_pulmonary_artery | heart | CardioVascular41.fbx | Left pulmonary artery, Superior lingular artery of left lung, Inferior lingular artery of left lung, Apical segmental artery of left lung (+7 more) | FMA50873 | 10298 | 6248 | 0.392 mm (limit 1) | 0.00 |
| right_pulmonary_veins | heart | CardioVascular41.fbx | Right superior pulmonary vein, Medial vein of right lung, Apical vein of right lung, Posterior vein of right lung (+6 more) | FMA66643 | 10491 | 5166 | 0.43 mm (limit 1) | 0.00 |
| left_pulmonary_veins | heart | CardioVascular41.fbx | Left superior pulmonary vein, Anterior vein of left lung, Apicoposterior vein of left lung, Inferior lingular vein of left lung (+6 more) | FMA66643 | 9132 | 4058 | 0.372 mm (limit 1) | 0.00 |
| esophagus | esophagus | VisceralSystem100.fbx | Oesophagus | FMA7131 | 8160 | 562 | 0.898 mm (limit 2) | 1.00 |
