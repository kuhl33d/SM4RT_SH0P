using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using System.Net.Sockets;

namespace hand_client
{
    public partial class Form1 : Form
    {
        Timer t = new Timer();
        Bitmap bg;
        double cx=-1, cy=-1,w=-1,h=-1;
        bool update = false;
        public Form1()
        {
            this.WindowState = FormWindowState.Maximized;
            t.Tick += T_Tick;
            this.Load += Form1_Load;
            this.Paint += Form1_Paint;
        }

        private void Form1_Paint(object sender, PaintEventArgs e)
        {
            bg.Dispose();
            bg = new Bitmap(ClientSize.Width, ClientSize.Height);
        }

        private void Form1_Load(object sender, EventArgs e)
        {
            bg = new Bitmap(ClientSize.Width,ClientSize.Height);

            t.Start();
        }

        private void T_Tick(object sender, EventArgs e)
        {
            try
            {
                using (TcpClient client = new TcpClient("127.0.0.1", 12345))
                using (NetworkStream stream = client.GetStream())
                {
                    Console.WriteLine("Connected to the server.");

                    while (true)
                    {
                        byte[] buffer = new byte[1024];
                        int bytesRead = stream.Read(buffer, 0, buffer.Length);

                        if (bytesRead == 0)
                        {
                            Console.WriteLine("Connection closed by the server.");
                            break;
                        }

                        string base64Data = Encoding.UTF8.GetString(buffer, 0, bytesRead);
                        byte[] decodedBytes = Convert.FromBase64String(base64Data);
                        string decodedData = Encoding.UTF8.GetString(decodedBytes);
                        this.Text = decodedData;
                        cx = int.Parse(decodedData.Split(',')[0]);
                        cy = int.Parse(decodedData.Split(',')[1]);
                        w = int.Parse(decodedData.Split(',')[2]);
                        h = int.Parse(decodedData.Split(',')[3]);
                        Console.WriteLine("Received data: " + decodedData);
                        update = true;
                    }
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine("Error: " + ex.Message);
            }

            draw(CreateGraphics());
        }

        void draw(Graphics g)
        {
            if (bg != null)
            {
                buffer(Graphics.FromImage(bg));
                g.DrawImage(bg, 0, 0);
            }
            g.Dispose();
        }
        void buffer(Graphics g)
        {
            //g.Clear(BackColor);
            if(cx != -1 && cy != -1 && update){
                cx /= w;
                cx *= ClientSize.Width;
                cy /= h;
                cx *= ClientSize.Height;
                g.FillRectangle(Brushes.Black, (int)cx - 10, (int)cy - 10, 20, 20);
                this.Text += " --> " + cx + " " + cy;
                update = false;
            }
            g.Dispose();
        }
    }
}
