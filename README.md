# Split_bam_into_HP
Split Bam file in to three isolated bam by using Haplotype tags (HP:i:1 or HP:i:2)

There are two step:
(1) Divide Input-Bam into 3 files:
 		'Haplotype 1 Bam'--'1.0.bam'
 		'Haplotype 2 Bam'--'2.0.bam'
		'Unphased Bam'   --'0.0.bam'
(2) Index and Sort 3 new Bam files (Require samtools env)

