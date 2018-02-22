import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';

@Component({
  selector: 'app-dash-header',
  templateUrl: './dash-header.component.html',
  styleUrls: ['./dash-header.component.css']
})
export class DashHeaderComponent implements OnInit {
  uID: string;
  buttons = [
    {'text': 'items'},
    {'text': 'holds'}
  ]
  
  constructor(private route: ActivatedRoute) {}
  
  ngOnInit() {
    this.uID = this.route.snapshot.firstChild.paramMap.get('uID');
  }

}
