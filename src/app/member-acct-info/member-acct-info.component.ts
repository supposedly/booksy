import { Component, OnInit, Input } from '@angular/core';

@Component({
  selector: 'app-member-acct-info',
  templateUrl: './member-acct-info.component.html',
  styleUrls: ['./member-acct-info.component.css']
})
export class MemberAcctInfoComponent implements OnInit {
  
  constructor() { }
  
  @Input() uID: string;
  
  ngOnChanges() {
  }
  
  ngOnInit() {
  }

}
