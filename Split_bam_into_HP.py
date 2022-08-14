
import os
import pysam
import argparse
import errno


def main():
    """
    Split Bam file in to three isolated bam by using Haplotype tags (HP:i:1 or HP:i:2)
    (1)Set the output files names
    (2)If User specified output dir,set output_file into direction
    (3)Input bam file: open input BAM file for reading
    (4)OUTput bam file : Set up the output BAM file for writing
    (5)Load samtools to sort & index output files by pysam (pysam module require samtools)
    """
    parser = argparse.ArgumentParser(description="1.Splits BAM file into three two BAM files;" \
                                                 "2.Generate 'HP:i:1','HP:i:0','Unsign' in to 3 BAM files：‘0.0.bam/’;" \
                                                 "3.sort and index new bam files;" \
                                                 "4.Caculate the percentage of HP 1&2.")
    parser.add_argument('-b', '--bam-file', dest='bam_file', required=True, help='Input BAM file (File name with pathway prefixe)')
    parser.add_argument('-o1', '--output1', dest='output1', required=False, help='Output BAM file #HP:1 (Optional)')
    parser.add_argument('-o2', '--output2', dest='output2', required=False, help='Output BAM file #HP:2 (Optional)')
    parser.add_argument('-o3', '--output3', dest='output3', required=False, help='Output BAM file #Unsign (Optional)')
    parser.add_argument('-d', '--output-dir', dest='output_dir', required=False, help='Output directory (Optional)')
    parser.add_argument('-h', '--haplotype_tag', dest='haplotype_tag', type=float, required=False, help='Haplotype tags (HP) in each reads are HP:i:1 or HP:i:2')
    args = parser.parse_args()
    print('#   Input Bam File  #')
    print(args.bam_file)

    #Os.path.isfile () : checks whether an object (with an absolute path) is a file
    #Os.path.isdir () : checks whether an object (with an absolute path) is a directory
    if not os.path.isfile(args.bam_file):
        print("ERROR: BAM file does not exist!")
        exit(-1)

    if args.haplotype_tag != 'HP':
        print("ERROR: haplotype_tag must be 'HP'")
        exit(-1)

    '''
    (1)Set the output files names
    os.path.split(path) : ('c:/bam_dir', 'test.bam')
    os.path.splitext(args.bam_file)[0] = 'c:/bam_dir/test'
    os.path.splitext(args.bam_file)[1] = '.bam'              : File extension name
    '''

    if not args.output1:
        output1_filename = os.path.splitext(args.bam_file)[0] + "_1.0" + os.path.splitext(args.bam_file)[1]
    else:
        output1_filename = args.output1
    if not args.output2:
        output2_filename = os.path.splitext(args.bam_file)[0] + "_2.0" + os.path.splitext(args.bam_file)[1]
    else:
        output2_filename = args.output2
    if not args.output3:
        output3_filename = os.path.splitext(args.bam_file)[0] + "_0.0" + os.path.splitext(args.bam_file)[1]
    else:
        output3_filename = args.output3
    print('#   Output bam files   #')
    print(output1_filename)
    print(output2_filename)
    print(output3_filename)

    '''
    (2)If User specified output dir,set output_file into direction
    '''
    if args.output_dir:
        # if it already exists, we join paths like
            # Os.path.isdir () : checks whether an object (with an absolute path) is a directory
        if os.path.isdir(args.output_dir):
            # Splice the string starting with the first one containing /:
            # os.path.join:(outdir,outputfile)
            # /outdir/testbam
            output1_filename = os.path.join(args.output_dir, output1_filename)
            output2_filename = os.path.join(args.output_dir, output2_filename)
            output3_filename = os.path.join(args.output_dir, output3_filename)

        # else try and create, then join
        else:
            try:
                os.makedirs(args.output_dir)
                output1_filename = os.path.join(args.output_dir, output1_filename)
                output2_filename = os.path.join(args.output_dir, output2_filename)
                output3_filename = os.path.join(args.output_dir, output3_filename)
            except OSError as exception:
                print('Error!  Wrong output direction fo bam files!')
                if exception.errno != errno.EEXIST:
                    raise


    ############  pysam  function ################################################
    """
    (3)Input bam file: open input BAM file for reading
    """
    bam_f = pysam.AlignmentFile(args.bam_file, "rb")
    num_read_1 = 0
    num_read_2 = 0
    num_read_3 = 0
    num_read_all = 0
    """
    (4)OUTput bam file : Set up the output BAM file for writing
        outputFile = pysam.AlignmentFile()
        outputFile=pysam.AlignmentFile(self.args.outputFile, outputFlags, header=inputFile.header)
    """
    output1_f = pysam.AlignmentFile(output1_filename, "wb", template=bam_f)
    output2_f = pysam.AlignmentFile(output2_filename, "wb", template=bam_f)
    output3_f = pysam.AlignmentFile(output3_filename, "wb", template=bam_f)


    #(4-1)set the iter of bam file for reading each read
    bam_iter = bam_f.fetch(until_eof=True)
    #(4-2)run process of pysam function ; find HP tag in each read of BAM file
    for read in bam_iter:
        num_read_all += 1
        if read.has_tag('HP'):
            i = read.get_tag('HP')
            if i == 1:
                output1_f.write(read)
                num_read_1 += 1
            if i == 2:
                output2_f.write(read)
                num_read_2 += 1
        else:
            output3_f.write(read)
            num_read_3 += 1

    bam_f.close()
    output1_f.close()
    output2_f.close()
    output3_f.close()


    """
    (5)Load samtools to sort & index output files by pysam(require samtools)
    """
    output1_filename_sort = os.path.splitext(output1_filename)[0]+'.sorted'+os.path.splitext(output1_filename)[1]
    output2_filename_sort = os.path.splitext(output2_filename)[0]+'.sorted'+os.path.splitext(output2_filename)[1]
    output3_filename_sort = os.path.splitext(output3_filename)[0]+'.sorted'+os.path.splitext(output3_filename)[1]
    pysam.sort("-o", output1_filename_sort, output1_filename)
    pysam.sort("-o", output2_filename_sort, output2_filename)
    pysam.sort("-o", output3_filename_sort, output3_filename)
    pysam.index(output1_filename_sort)
    pysam.index(output2_filename_sort)
    pysam.index(output3_filename_sort)
    print('#   Finish sort & index   #')
    print(output1_filename_sort)
    print(output2_filename_sort)
    print(output3_filename_sort)
    print('#   Satistic   #')
    print('HP:1' + ' ' + str(num_read_1) + ' ' +str(num_read_1/num_read_all)+'%')
    print('HP:2' + ' ' + str(num_read_2) + ' ' +str(num_read_2/num_read_all)+'%')
    print('Unsigned' + ' ' + str(num_read_3) + ' ' +str(num_read_3/num_read_all)+'%')



if __name__ == "__main__":
    main()






